from flask import jsonify, Blueprint, request
import jwt
import os
from api.Models.Base import SessionLocal
from api.Models.SeguirViendo import SeguirViendo

seguir_viendo_bp = Blueprint("seguir_viendo", __name__)

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

def _get_user_id():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, (jsonify({"error": "Token no proporcionat"}), 401)
    try:
        payload = jwt.decode(auth[7:], JWT_SECRET, algorithms=[JWT_ALGORITHM])
        uid = payload.get("id")
        if not uid:
            return None, (jsonify({"error": "Token invàlid"}), 401)
        return uid, None
    except jwt.ExpiredSignatureError:
        return None, (jsonify({"error": "Token expirat"}), 401)
    except jwt.InvalidTokenError:
        return None, (jsonify({"error": "Token invàlid"}), 401)

@seguir_viendo_bp.get("/api/seguir_viendo")
def get_seguir_viendo():
    user_id, err = _get_user_id()
    if err:
        return err
    db = SessionLocal()
    try:
        # Order by updated_at descending so the most recently watched is first
        items = db.query(SeguirViendo).filter(SeguirViendo.user_id == user_id).order_by(SeguirViendo.updated_at.desc()).all()
        return jsonify([i.to_dict() for i in items])
    finally:
        db.close()

@seguir_viendo_bp.post("/api/seguir_viendo")
def add_or_update_seguir_viendo():
    user_id, err = _get_user_id()
    if err:
        return err
    data = request.get_json() or {}
    tmdb_id = data.get("tmdb_id") or data.get("id")
    media_type = data.get("media_type", "movie")
    if not tmdb_id:
        return jsonify({"error": "tmdb_id requerit"}), 400

    db = SessionLocal()
    try:
        existing = db.query(SeguirViendo).filter_by(
            user_id=user_id, tmdb_id=tmdb_id, media_type=media_type
        ).first()

        if existing:
            # Update existing
            if "progress" in data:
                existing.progress = data.get("progress")
            if "duration" in data:
                existing.duration = data.get("duration")
            db.commit()
            db.refresh(existing)
            return jsonify(existing.to_dict()), 200

        # Create new
        item = SeguirViendo(
            user_id=user_id,
            tmdb_id=tmdb_id,
            media_type=media_type,
            title=data.get("title") or data.get("name"),
            poster_path=data.get("poster_path"),
            backdrop_path=data.get("backdrop_path"),
            progress=data.get("progress", 0.0),
            duration=data.get("duration", 0.0)
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return jsonify(item.to_dict()), 201
    finally:
        db.close()

@seguir_viendo_bp.delete("/api/seguir_viendo/<int:tmdb_id>/<string:media_type>")
def remove_from_seguir_viendo(tmdb_id, media_type):
    user_id, err = _get_user_id()
    if err:
        return err
    db = SessionLocal()
    try:
        item = db.query(SeguirViendo).filter_by(
            user_id=user_id, tmdb_id=tmdb_id, media_type=media_type
        ).first()
        if not item:
            return jsonify({"error": "No trobat"}), 404
        db.delete(item)
        db.commit()
        return jsonify({"ok": True})
    finally:
        db.close()
