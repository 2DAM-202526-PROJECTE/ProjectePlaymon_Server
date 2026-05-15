from flask import Blueprint, jsonify, request
from api.Models.Base import SessionLocal
from api.Services.NotificationService import NotificationService, VALID_TYPES
from api.Events.sse_broker import broadcast_notification
from api.Utils.auth import require_admin

notification_create_bp = Blueprint("notification_create", __name__)


@notification_create_bp.post("/api/notifications")
def create_notification():
    payload, err = require_admin()
    if err:
        return jsonify(err[0]), err[1]

    data = request.get_json(silent=True) or {}
    type_ = data.get("type", "").strip()
    title = data.get("title", "").strip()
    body = data.get("body", "").strip()
    target_user_id = data.get("target_user_id")  # null = broadcast

    if type_ not in VALID_TYPES:
        return jsonify({"error": f"Tipus invàlid. Valors acceptats: {', '.join(VALID_TYPES)}"}), 400
    if not title:
        return jsonify({"error": "El camp 'title' és obligatori"}), 400
    if not body:
        return jsonify({"error": "El camp 'body' és obligatori"}), 400
    if type_ == "message" and not target_user_id:
        return jsonify({"error": "Els missatges privats requereixen 'target_user_id'"}), 400

    db = SessionLocal()
    try:
        notif = NotificationService.create(
            db,
            type=type_,
            title=title,
            body=body,
            sender_id=payload.get("id"),
            target_user_id=target_user_id,
        )
        broadcast_notification(notif.id, notif.type, notif.target_user_id)
        return jsonify(notif.to_dict()), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": "Error creant notificació", "detail": str(e)}), 500
    finally:
        db.close()
