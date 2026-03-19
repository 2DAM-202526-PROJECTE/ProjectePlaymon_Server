from flask import jsonify, Blueprint
from api.Models.Base import SessionLocal
from api.Services.PeliService import PeliService

peli_get_bp = Blueprint("peli_get", __name__)

@peli_get_bp.get("/api/pelis")
def get_pelis():
    from flask import request
    categoria = request.args.get("categoria")
    db = SessionLocal()
    try:
        pelis = PeliService.get_all(db, categoria)
        return jsonify([p.to_dict() for p in pelis])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@peli_get_bp.get("/api/pelis/<int:peli_id>")
def get_peli(peli_id):
    db = SessionLocal()
    try:
        peli = PeliService.get_by_id(db, peli_id)
        if not peli:
            return jsonify({"error": "Pel·lícula no trobada"}), 404
        return jsonify(peli.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
