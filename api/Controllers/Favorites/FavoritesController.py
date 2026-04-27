from flask import jsonify, Blueprint, request
import jwt
import os
from api.Models.Base import SessionLocal
from api.Models.Favorite import Favorite

favorites_bp = Blueprint("favorites", __name__)

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


@favorites_bp.get("/api/favorites")
def get_favorites():
    user_id, err = _get_user_id()
    if err:
        return err
    db = SessionLocal()
    try:
        favs = db.query(Favorite).filter(Favorite.user_id == user_id).all()
        return jsonify([f.to_dict() for f in favs])
    finally:
        db.close()


@favorites_bp.post("/api/favorites")
def add_favorite():
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
        existing = db.query(Favorite).filter_by(
            user_id=user_id, tmdb_id=tmdb_id, media_type=media_type
        ).first()
        if existing:
            return jsonify(existing.to_dict()), 200

        fav = Favorite(
            user_id=user_id,
            tmdb_id=tmdb_id,
            media_type=media_type,
            title=data.get("title") or data.get("name"),
            poster_path=data.get("poster_path"),
            backdrop_path=data.get("backdrop_path"),
            overview=data.get("overview"),
            release_date=data.get("release_date"),
            first_air_date=data.get("first_air_date"),
            vote_average=data.get("vote_average"),
            genres=data.get("genres", []),
        )
        db.add(fav)
        db.commit()
        db.refresh(fav)
        return jsonify(fav.to_dict()), 201
    finally:
        db.close()


@favorites_bp.delete("/api/favorites/<int:tmdb_id>/<string:media_type>")
def remove_favorite(tmdb_id, media_type):
    user_id, err = _get_user_id()
    if err:
        return err
    db = SessionLocal()
    try:
        fav = db.query(Favorite).filter_by(
            user_id=user_id, tmdb_id=tmdb_id, media_type=media_type
        ).first()
        if not fav:
            return jsonify({"error": "No trobat"}), 404
        db.delete(fav)
        db.commit()
        return jsonify({"ok": True})
    finally:
        db.close()
