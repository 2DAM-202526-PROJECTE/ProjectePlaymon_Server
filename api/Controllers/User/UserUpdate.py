from flask import jsonify, Blueprint, request
from werkzeug.security import generate_password_hash
from api.Models.Base import SessionLocal
from api.Services.UserService import UserService
from api.Events.sse_broker import broadcast_user_updated
import sqlalchemy.exc

user_update_bp = Blueprint("user_update", __name__)


@user_update_bp.put("/api/users/<int:user_id>")
def update_user(user_id):
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"message": "Cap camp per actualitzar"}), 200

    valid_keys = ["username", "name", "email", "role", "avatar", "pla_pagament", "is_active"]
    update_data = {k: data[k] for k in valid_keys if k in data}

    if "password" in data:
        update_data["password_hash"] = generate_password_hash(data["password"].strip())

    if "subscription_plan" in data and "pla_pagament" not in update_data:
        update_data["pla_pagament"] = data["subscription_plan"]

    if "pla_pagament" in update_data:
        plan = (update_data["pla_pagament"] or "basic").strip().lower()
        if plan not in ("basic", "super", "master", "ultra"):
            return jsonify({"error": "Pla de subscripció invàlid (basic/super/master/ultra)"}), 400
        update_data["pla_pagament"] = plan

    if not update_data:
        return jsonify({"message": "Cap camp vàlid per actualitzar"}), 200

    db = SessionLocal()
    try:
        user = UserService.update(db, user_id, update_data)
        if not user:
            return jsonify({"error": "Usuari no trobat"}), 404

        broadcast_user_updated(user_id)
        return jsonify(user.to_dict()), 200

    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        return jsonify({"error": "username o email ja existeix"}), 409
    except Exception as e:
        db.rollback()
        return jsonify({"error": "Error BD", "detail": str(e)}), 500
    finally:
        db.close()
