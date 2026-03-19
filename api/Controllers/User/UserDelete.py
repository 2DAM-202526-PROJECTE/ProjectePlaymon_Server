from flask import jsonify, Blueprint
from api.Models.Base import SessionLocal
from api.Services.UserService import UserService

user_delete_bp = Blueprint("user_delete", __name__)

@user_delete_bp.delete("/api/users/<int:user_id>")
def delete_user(user_id):
    db = SessionLocal()
    try:
        success = UserService.delete(db, user_id)
        if success:
            return jsonify({"deleted": user_id}), 200
        return jsonify({"error": "Usuari no trobat"}), 404
    except Exception as e:
        db.rollback()
        return jsonify({"error": "Error eliminant usuari", "detail": str(e)}), 500
    finally:
        db.close()
