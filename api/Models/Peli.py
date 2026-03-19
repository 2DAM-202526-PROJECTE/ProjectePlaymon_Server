from sqlalchemy import Column, Integer, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSON
from .Base import Base

class Peli(Base):
    __tablename__ = "pelicules"

    # NOTE: In the provided SQL, 'id' doesn't have a primary key constraint, 
    # but SQLAlchemy requires one. Assuming 'id' is the unique identifier.
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    title = Column(Text)
    description = Column(Text)
    video_url = Column(Text)
    poster_path = Column(Text)
    backdrop_url = Column(Text)
    duration = Column(Integer)
    file_size = Column(Integer)
    is_public = Column(Boolean)
    categoria = Column(JSON)
    reparto = Column(JSON)
    direccio = Column(JSON)
    fecha_estreno = Column(DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "video_url": self.video_url,
            "poster_path": self.poster_path,
            "backdrop_url": self.backdrop_url,
            "duration": self.duration,
            "file_size": self.file_size,
            "is_public": self.is_public,
            "categoria": self.categoria,
            "reparto": self.reparto,
            "direccio": self.direccio,
            "fecha_estreno": self.fecha_estreno.isoformat() if hasattr(self.fecha_estreno, 'isoformat') else self.fecha_estreno,
        }
