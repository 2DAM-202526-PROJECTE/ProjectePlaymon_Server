from sqlalchemy import Column, BigInteger, Text, DateTime, UniqueConstraint, func
from .Base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(Text, nullable=False)  # 'news' | 'update' | 'message'
    title = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    target_user_id = Column(BigInteger, nullable=True)  # null = broadcast to all
    sender_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "body": self.body,
            "target_user_id": self.target_user_id,
            "sender_id": self.sender_id,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else self.created_at,
        }


class NotificationRead(Base):
    __tablename__ = "notification_reads"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    notification_id = Column(BigInteger, nullable=False)
    read_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "notification_id"),)
