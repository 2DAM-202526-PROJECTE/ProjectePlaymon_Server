from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from api.Models.Peli import Peli
from typing import List, Optional

class PeliService:
    @staticmethod
    def get_all(db: Session, categoria: str = None) -> List[Peli]:
        query = db.query(Peli)
        
        if categoria:
            # We filter for the presence of the category ID/name in the JSON column.
            # Casting to String and searching for the string representation of the ID/name
            # is a broadly compatible way to search inside JSON arrays for now.
            query = query.filter(cast(Peli.categoria, String).contains(categoria))
            
        return query.order_by(Peli.id.desc()).all()

    @staticmethod
    def get_by_id(db: Session, peli_id: int) -> Optional[Peli]:
        return db.query(Peli).filter(Peli.id == peli_id).first()

    @staticmethod
    def create(db: Session, data: dict) -> Peli:
        peli = Peli(**data)
        db.add(peli)
        db.commit()
        db.refresh(peli)
        return peli

    @staticmethod
    def update(db: Session, peli_id: int, data: dict) -> Optional[Peli]:
        peli = db.query(Peli).filter(Peli.id == peli_id).first()
        if not peli:
            return None
        
        for key, value in data.items():
            if hasattr(peli, key):
                setattr(peli, key, value)
        
        db.commit()
        db.refresh(peli)
        return peli

    @staticmethod
    def delete(db: Session, peli_id: int) -> bool:
        peli = db.query(Peli).filter(Peli.id == peli_id).first()
        if not peli:
            return False
        
        db.delete(peli)
        db.commit()
        return True
