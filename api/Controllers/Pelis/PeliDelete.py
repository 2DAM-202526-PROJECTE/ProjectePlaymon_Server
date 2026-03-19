from flask import jsonify, Blueprint
from api.Models.Base import SessionLocal
from api.Services.PeliService import PeliService

peli_delete_bp = Blueprint("peli_delete", __name__)

@peli_delete_bp.delete("/api/pelis/<int:peli_id>")
def delete_peli(peli_id):
    db = SessionLocal()
    try:
        success = PeliService.delete(db, peli_id)
        if success:
            return jsonify({"deleted": peli_id}), 200
        return jsonify({"error": "Pel·lícula no trobada"}), 404
    except Exception as e:
        db.rollback()
        return jsonify({"error": "Error eliminant la pel·lícula", "detail": str(e)}), 500
    finally:
        db.close()
