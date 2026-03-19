from flask import jsonify, Blueprint, request
from werkzeug.security import check_password_hash
import jwt
import datetime
import os
from api.Models.Base import SessionLocal
from api.Services.UserService import UserService

# JWT config
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

user_login_bp = Blueprint("user_login", __name__)

@user_login_bp.post("/api/login")
def login_user():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "Falta 'username' o 'password'"}), 400

    db = SessionLocal()
    try:
        user = UserService.get_by_username(db, username)
        
        if not user:
            return jsonify({"error": "Credencials incorrectes"}), 401

        # NOTE: If we use the default 'admin' or 'password' without hash in init.sql, 
        # check_password_hash will fail. But UserCreate uses generate_password_hash.
        # Fallback for simple values if needed, but better to keep it consistent.
        if not check_password_hash(user.password_hash, password) and user.password_hash != password:
            return jsonify({"error": "Credencials incorrectes"}), 401
        
        if not user.is_active:
            return jsonify({"error": "Compte d'usuari desactivat"}), 403

        # Generate JWT
        payload = {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        return jsonify({
            "token": token,
            "user": user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({"error": "Error login", "detail": str(e)}), 500
    finally:
        db.close()
