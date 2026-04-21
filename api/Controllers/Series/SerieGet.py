from flask import jsonify, Blueprint, request
from api.Models.Base import SessionLocal
from api.Services.SerieService import SerieService

serie_get_bp = Blueprint("serie_get", __name__)

@serie_get_bp.get("/api/series")
def get_series():
    categoria = request.args.get("categoria")
    db = SessionLocal()
    try:
        series = SerieService.get_all(db, categoria)
        return jsonify([s.to_dict() for s in series])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@serie_get_bp.get("/api/series/<int:serie_id>")
def get_serie(serie_id):
    db = SessionLocal()
    try:
        serie = SerieService.get_by_id(db, serie_id)
        if not serie:
            return jsonify({"error": "Sèrie no trobada"}), 404
        return jsonify(serie.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@serie_get_bp.get("/api/series/<int:serie_id>/relacionats")
def get_series_relacionats(serie_id):
    """Retorna fins a 12 sèries del mateix gènere, excloent la sèrie actual."""
    db = SessionLocal()
    try:
        from api.Models.Serie import Serie
        from sqlalchemy import cast, String
        serie = db.query(Serie).filter(Serie.id == serie_id).first()
        if not serie:
            return jsonify([])

        cats = serie.categoria or []
        if isinstance(cats, str):
            import json
            try: cats = json.loads(cats)
            except: cats = []

        if not cats:
            series = db.query(Serie).filter(
                Serie.id != serie_id,
                Serie.is_public == True
            ).order_by(Serie.id.desc()).limit(12).all()
            return jsonify([s.to_dict() for s in series])

        first_genre = cats[0]
        search_term = str(first_genre.get("id", "")) if isinstance(first_genre, dict) else str(first_genre)

        series = db.query(Serie).filter(
            Serie.id != serie_id,
            Serie.is_public == True,
            cast(Serie.categoria, String).contains(search_term)
        ).order_by(Serie.id.desc()).limit(12).all()

        return jsonify([s.to_dict() for s in series])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@serie_get_bp.get("/api/series/search")
def search_local_series():
    from flask import request
    query = request.args.get("query", "")
    db = SessionLocal()
    try:
        from api.Models.Serie import Serie
        import unicodedata
        from sqlalchemy import func
        if not query:
            return jsonify([])
            
        # Normalitzem accents
        nfkd = unicodedata.normalize('NFKD', query)
        query_unaccent = "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()
        
        accents = 'áéíóúàèìòùäëïöüâêîôûñÁÉÍÓÚÀÈÌÒÙÄËÏÖÜÂÊÎÔÛÑ'
        base    = 'aeiouaeiouaeiouaeiounAEIOUAEIOUAEIOUAEIOUN'
        
        series = db.query(Serie).filter(
            Serie.is_public == True,
            func.translate(Serie.title, accents, base).ilike(f"{query_unaccent}%")
        ).order_by(Serie.title.asc()).limit(20).all()
        return jsonify([s.to_dict() for s in series])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
