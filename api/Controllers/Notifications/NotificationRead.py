from flask import Blueprint, jsonify
from api.Models.Base import SessionLocal
from api.Services.NotificationService import NotificationService
from api.Utils.auth import decode_jwt

notification_read_bp = Blueprint("notification_read", __name__)


@notification_read_bp.post("/api/notifications/<int:notification_id>/read")
def mark_read(notification_id):
    payload, err = decode_jwt()
    if err:
        return jsonify(err[0]), err[1]

    user_id = payload.get("id")
    db = SessionLocal()
    try:
        notif = NotificationService.get_by_id(db, notification_id)
        if not notif:
            return jsonify({"error": "Notificació no trobada"}), 404
        if notif.target_user_id is not None and notif.target_user_id != user_id:
            return jsonify({"error": "Accés denegat"}), 403
        NotificationService.mark_read(db, user_id, notification_id)
        return jsonify({"ok": True}), 200
    except Exception as e:
        return jsonify({"error": "Error marcant com a llegida", "detail": str(e)}), 500
    finally:
        db.close()


@notification_read_bp.post("/api/notifications/read-all")
def mark_all_read():
    payload, err = decode_jwt()
    if err:
        return jsonify(err[0]), err[1]

    user_id = payload.get("id")
    db = SessionLocal()
    try:
        count = NotificationService.mark_all_read(db, user_id)
        return jsonify({"ok": True, "marked": count}), 200
    except Exception as e:
        return jsonify({"error": "Error marcant totes com a llegides", "detail": str(e)}), 500
    finally:
        db.close()
