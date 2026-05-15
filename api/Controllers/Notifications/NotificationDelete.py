from flask import Blueprint, jsonify
from api.Models.Base import SessionLocal
from api.Services.NotificationService import NotificationService
from api.Utils.auth import require_admin

notification_delete_bp = Blueprint("notification_delete", __name__)


@notification_delete_bp.delete("/api/notifications/<int:notification_id>")
def delete_notification(notification_id):
    payload, err = require_admin()
    if err:
        return jsonify(err[0]), err[1]

    db = SessionLocal()
    try:
        deleted = NotificationService.delete(db, notification_id)
        if not deleted:
            return jsonify({"error": "Notificació no trobada"}), 404
        return jsonify({"ok": True}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": "Error eliminant notificació", "detail": str(e)}), 500
    finally:
        db.close()
