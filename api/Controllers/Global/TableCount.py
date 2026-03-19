from flask import Blueprint, jsonify
from api.Models.Base import engine
from sqlalchemy import text

table_count_bp = Blueprint("table_count", __name__)

@table_count_bp.get("/api/stats/<string:table_name>/count")
def get_table_count(table_name):
    # Dynamic table name check for security
    allowed_tables = ["users", "videos", "pelicules"]
    if table_name not in allowed_tables:
        return jsonify({"error": "Taula no trobada o no permesa"}), 404

    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            total = result.scalar()

        return jsonify({
            "table": table_name,
            "count": total,
        }), 200
    except Exception as e:
        return jsonify({"error": "Error obtenint recompte", "detail": str(e)}), 500