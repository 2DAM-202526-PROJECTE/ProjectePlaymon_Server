from flask import jsonify, Blueprint
from db import fetch_one

user_delete_bp = Blueprint("user_delete", __name__)

@user_delete_bp.delete("/api/users/<int:user_id>")
def delete_user(user_id):
    row = fetch_one(
        "DELETE FROM users WHERE id = %s RETURNING id;",
        (user_id,)
    )
    if not row:
        return jsonify({"error": "Usuari no trobat"}), 404
    return jsonify({"deleted": row[0]})
