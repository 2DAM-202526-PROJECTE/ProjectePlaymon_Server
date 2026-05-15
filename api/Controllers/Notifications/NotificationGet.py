from flask import Blueprint, jsonify
from api.Models.Base import SessionLocal
from api.Services.NotificationService import NotificationService
from api.Utils.auth import decode_jwt

notification_get_bp = Blueprint("notification_get", __name__)


@notification_get_bp.get("/api/notifications")
def get_notifications():
    payload, err = decode_jwt()
    if err:
        return jsonify(err[0]), err[1]

    user_id = payload.get("id")
    db = SessionLocal()
    try:
        notifications = NotificationService.get_for_user(db, user_id)
        return jsonify(notifications), 200
    except Exception as e:
        return jsonify({"error": "Error obtenint notificacions", "detail": str(e)}), 500
    finally:
        db.close()


@notification_get_bp.get("/api/notifications/unread-count")
def get_unread_count():
    payload, err = decode_jwt()
    if err:
        return jsonify(err[0]), err[1]

    user_id = payload.get("id")
    db = SessionLocal()
    try:
        count = NotificationService.unread_count(db, user_id)
        return jsonify({"count": count}), 200
    except Exception as e:
        return jsonify({"error": "Error comptant notificacions", "detail": str(e)}), 500
    finally:
        db.close()
