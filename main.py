# main.py
from dotenv import load_dotenv
load_dotenv()  # IMPORTANT: abans d'importar db

from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg

from db import fetch_all, execute_one

app = Flask(__name__)
CORS(app)

# Camps que retornarem (controlat i consistent)
USER_SELECT = "id, username, name, email, role, is_active, created_at, updated_at"

@app.get("/api/users")
def get_users():
    rows = fetch_all(f"SELECT {USER_SELECT} FROM users ORDER BY id;")
    # rows ja són dicts (db.py usa dict_row)
    return jsonify(rows), 200

@app.post("/api/users")
def create_user():
    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip()
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    role = (data.get("role") or "user").strip()

    if not username or not name or not email:
        return jsonify({"error": "Falten camps: username, name, email"}), 400

    try:
        row = execute_one(
            f"""
            INSERT INTO users (username, name, email, role, is_active)
            VALUES (%s, %s, %s, %s, true)
            RETURNING {USER_SELECT};
            """,
            (username, name, email, role),
        )
        return jsonify(row), 201

    except psycopg.errors.UniqueViolation:
        # Si tens UNIQUE a username/email
        return jsonify({"error": "Ja existeix un usuari amb aquest username o email"}), 409

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
