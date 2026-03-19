from sqlalchemy import Column, Integer, BigInteger, Text, Boolean, DateTime, Date, ForeignKey, func
from .Base import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    video_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text)
    duration = Column(Integer)
    file_size = Column(BigInteger)
    is_public = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    categoria = Column(Text)
    reparto = Column(Text)
    direccio = Column(Text)
    calificacio = Column(Integer)
    fecha_estreno = Column(Date)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "video_url": self.video_url,
            "thumbnail_url": self.thumbnail_url,
            "duration": self.duration,
            "file_size": self.file_size,
            "is_public": self.is_public,
            "categoria": self.categoria,
            "reparto": self.reparto,
            "direccio": self.direccio,
            "calificacio": self.calificacio,
            "fecha_estreno": self.fecha_estreno.isoformat() if hasattr(self.fecha_estreno, 'isoformat') else self.fecha_estreno,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else self.created_at,
            "updated_at": self.updated_at.isoformat() if hasattr(self.updated_at, 'isoformat') else self.updated_at,
        }
