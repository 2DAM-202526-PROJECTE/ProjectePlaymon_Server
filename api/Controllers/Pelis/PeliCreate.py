from flask import jsonify, Blueprint, request
from api.Models.Base import SessionLocal
from api.Services.PeliService import PeliService
import sqlalchemy.exc

peli_create_bp = Blueprint("peli_create", __name__)

@peli_create_bp.post("/api/pelis")
def create_peli():
    data = request.get_json(silent=True) or {}
    
    # Required attributes based on the new schema
    peli_id = data.get("id")
    title = data.get("title")
    
    if peli_id is None:
        return jsonify({"error": "Falta 'id'"}), 400
    if not title:
        return jsonify({"error": "Falta 'title'"}), 400

    # Filter data to match new schema keys
    valid_keys = [
        "id", "user_id", "title", "description", "video_url", 
        "poster_path", "backdrop_url", "duration", "file_size", 
        "is_public", "categoria", "reparto", "direccio", "fecha_estreno"
    ]
    peli_data = {k: data[k] for k in valid_keys if k in data}

    db = SessionLocal()
    try:
        peli = PeliService.create(db, peli_data)
        return jsonify(peli.to_dict()), 201
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        return jsonify({"error": f"L'ID de la pel·lícula {peli_id} ja existeix"}), 409
    except Exception as e:
        db.rollback()
        return jsonify({"error": "Error creant la pel·lícula", "detail": str(e)}), 500
    finally:
        db.close()
