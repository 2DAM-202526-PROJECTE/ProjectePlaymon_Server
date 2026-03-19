from flask import jsonify, Blueprint, request
import jwt
import os
from api.Models.Base import SessionLocal
from api.Services.UserService import UserService

user_get_bp = Blueprint("user_get", __name__)

# JWT Secret - must match the one in UserLogin.py
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

@user_get_bp.get("/api/users")
def get_users():
    db = SessionLocal()
    try:
        users = UserService.get_all(db)
        return jsonify([u.to_dict() for u in users])
    finally:
        db.close()

@user_get_bp.get("/api/users/<int:user_id>")
def get_user(user_id):
    db = SessionLocal()
    try:
        user = UserService.get_by_id(db, user_id)
        if not user:
            return jsonify({"error": "Usuari no trobat"}), 404
        return jsonify(user.to_dict())
    finally:
        db.close()

@user_get_bp.get("/api/users/me")
def get_current_user():
    try:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token no proporcionat"}), 401
        
        token = auth_header[7:]
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("id")
        
        if not user_id:
            return jsonify({"error": "Token inválid"}), 401
        
        db = SessionLocal()
        try:
            user = UserService.get_by_id(db, user_id)
            if not user:
                return jsonify({"error": "Usuari no trobat"}), 404
            return jsonify(user.to_dict()), 200
        finally:
            db.close()
    
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirat"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválid"}), 401
    except Exception as e:
        return jsonify({"error": "Error obtenint usuari actual", "detail": str(e)}), 500
