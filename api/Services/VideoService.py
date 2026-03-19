from sqlalchemy.orm import Session
from api.Models.Video import Video
from typing import List, Optional

class VideoService:
    @staticmethod
    def get_public_videos(db: Session, limit: int = 20, offset: int = 0) -> List[Video]:
        return db.query(Video).filter(Video.is_public == True).order_by(Video.created_at.desc()).limit(limit).offset(offset).all()

    @staticmethod
    def get_user_videos(db: Session, user_id: int, limit: int = 20, offset: int = 0) -> List[Video]:
        return db.query(Video).filter(Video.user_id == user_id, Video.is_public == True).order_by(Video.created_at.desc()).limit(limit).offset(offset).all()

    @staticmethod
    def get_by_id(db: Session, video_id: int) -> Optional[Video]:
        return db.query(Video).filter(Video.id == video_id).first()

    @staticmethod
    def create(db: Session, data: dict) -> Video:
        video = Video(**data)
        db.add(video)
        db.commit()
        db.refresh(video)
        return video

    @staticmethod
    def delete(db: Session, video_id: int) -> bool:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return False
        db.delete(video)
        db.commit()
        return True
