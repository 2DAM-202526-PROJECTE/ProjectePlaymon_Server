from flask import jsonify, Blueprint, request
from werkzeug.security import generate_password_hash
from api.Models.Base import SessionLocal
from api.Services.UserService import UserService
import sqlalchemy.exc

user_create_bp = Blueprint("user_create", __name__)

def parse_bool(v, default=True):
    if v is None:
        return default
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("true", "1", "yes", "y", "si", "sí"):
            return True
        if s in ("false", "0", "no", "n"):
            return False
    return default

@user_create_bp.post("/api/users")
def create_user():
    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip()
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    role = (data.get("role") or "user").strip()
    is_active = parse_bool(data.get("is_active"), True)

    # Per proves: acceptem "password" i la guardem hashejada
    password = (data.get("password") or "password").strip()
    password_hash = generate_password_hash(password)
    pla_pagament = (data.get("pla_pagament") or "basic").strip()

    if not username:
        return jsonify({"error": "Falta 'username'"}), 400
    if not name:
        return jsonify({"error": "Falta 'name'"}), 400
    if not email:
        return jsonify({"error": "Falta 'email'"}), 400
    if role not in ("admin", "support", "user"):
        return jsonify({"error": "role invàlid (admin/support/user)"}), 400

    db = SessionLocal()
    try:
        user_data = {
            "username": username,
            "name": name,
            "email": email,
            "role": role,
            "is_active": is_active,
            "password_hash": password_hash,
            "pla_pagament": pla_pagament
        }
        user = UserService.create(db, user_data)
        return jsonify(user.to_dict()), 201

    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        return jsonify({"error": "username o email ja existeix"}), 409
    except Exception as e:
        db.rollback()
        return jsonify({"error": "Error BD", "detail": str(e)}), 500
    finally:
        db.close()
