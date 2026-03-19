from flask import jsonify, Blueprint, request
from api.Models.Base import SessionLocal
from api.Services.PeliService import PeliService
from datetime import datetime

peli_update_bp = Blueprint("peli_update", __name__)

@peli_update_bp.put("/api/pelis/<int:peli_id>")
def update_peli(peli_id):
    data = request.get_json(silent=True) or {}
    
    if not data:
        return jsonify({"error": "No s'han enviat dades per actualitzar"}), 400

    # Filter data to match new schema keys
    valid_keys = [
        "user_id", "title", "description", "video_url", "poster_path", 
        "backdrop_url", "duration", "file_size", "is_public", 
        "categoria", "reparto", "direccio", "fecha_estreno"
    ]
    peli_data = {k: data[k] for k in valid_keys if k in data}

    # Date parsing (now 'timestamp' in schema)
    if "fecha_estreno" in peli_data and isinstance(peli_data["fecha_estreno"], str):
        try:
            # Try ISO format
            peli_data["fecha_estreno"] = datetime.fromisoformat(peli_data["fecha_estreno"])
        except ValueError:
            pass

    if not peli_data:
        return jsonify({"message": "Cap camp vàlid per actualitzar"}), 200

    db = SessionLocal()
    try:
        updated_peli = PeliService.update(db, peli_id, peli_data)
        if not updated_peli:
            return jsonify({"error": "Pel·lícula no trobada"}), 404
        return jsonify(updated_peli.to_dict())
    except Exception as e:
        db.rollback()
        return jsonify({"error": "Error actualitzant la pel·lícula", "detail": str(e)}), 500
    finally:
        db.close()
