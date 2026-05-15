from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.Models.Notification import Notification, NotificationRead

VALID_TYPES = ("news", "update", "message")


class NotificationService:
    @staticmethod
    def create(db: Session, type: str, title: str, body: str, sender_id: int, target_user_id: int = None) -> Notification:
        notif = Notification(
            type=type,
            title=title,
            body=body,
            sender_id=sender_id,
            target_user_id=target_user_id,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

    @staticmethod
    def get_for_user(db: Session, user_id: int) -> list[dict]:
        notifs = (
            db.query(Notification)
            .filter(or_(Notification.target_user_id == None, Notification.target_user_id == user_id))
            .order_by(Notification.created_at.desc())
            .all()
        )

        read_ids = {
            r.notification_id
            for r in db.query(NotificationRead).filter(NotificationRead.user_id == user_id).all()
        }

        result = []
        for n in notifs:
            d = n.to_dict()
            d["is_read"] = n.id in read_ids
            result.append(d)
        return result

    @staticmethod
    def unread_count(db: Session, user_id: int) -> int:
        notif_ids = [
            n.id
            for n in db.query(Notification.id)
            .filter(or_(Notification.target_user_id == None, Notification.target_user_id == user_id))
            .all()
        ]
        if not notif_ids:
            return 0
        read_count = (
            db.query(NotificationRead)
            .filter(NotificationRead.user_id == user_id, NotificationRead.notification_id.in_(notif_ids))
            .count()
        )
        return len(notif_ids) - read_count

    @staticmethod
    def mark_read(db: Session, user_id: int, notification_id: int) -> None:
        try:
            db.add(NotificationRead(user_id=user_id, notification_id=notification_id))
            db.commit()
        except IntegrityError:
            db.rollback()

    @staticmethod
    def mark_all_read(db: Session, user_id: int) -> int:
        notifs = (
            db.query(Notification)
            .filter(or_(Notification.target_user_id == None, Notification.target_user_id == user_id))
            .all()
        )
        read_ids = {
            r.notification_id
            for r in db.query(NotificationRead).filter(NotificationRead.user_id == user_id).all()
        }
        count = 0
        for n in notifs:
            if n.id not in read_ids:
                db.add(NotificationRead(user_id=user_id, notification_id=n.id))
                count += 1
        db.commit()
        return count

    @staticmethod
    def get_all(db: Session) -> list[Notification]:
        return db.query(Notification).order_by(Notification.created_at.desc()).all()

    @staticmethod
    def get_by_id(db: Session, notification_id: int):
        return db.query(Notification).filter(Notification.id == notification_id).first()

    @staticmethod
    def delete(db: Session, notification_id: int) -> bool:
        notif = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notif:
            return False
        db.delete(notif)
        db.commit()
        return True
