from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from db import fetch_all, fetch_one  

app = Flask(__name__)
CORS(app)

@app.get("/")
def root():
    return "API OK (Postgres en marxa)"

@app.get("/api/users")
def get_users():
    rows = fetch_all("SELECT id, name FROM users ORDER BY id;")
    return jsonify([{"id": r[0], "name": r[1]} for r in rows])

@app.get("/api/users/<int:user_id>")
def get_user(user_id):
    row = fetch_one(
        "SELECT id, name FROM users WHERE id = %s;",
        (user_id,)
    )

    if not row:
        return jsonify({"error": "Usuari no trobat"}), 404

    return jsonify({"id": row[0], "name": row[1]})

@app.delete("/api/users/<int:user_id>")
def delete_user(user_id):
    row = fetch_one(
        "DELETE FROM users WHERE id = %s RETURNING id;",
        (user_id,)
    )

    if not row:
        return jsonify({"error": "Usuari no trobat"}), 404

    return jsonify({"deleted": row[0]})

@app.put("/api/users/<int:user_id>")
def update_user(user_id):
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()

    if not name:
        return jsonify({"error": "Falta 'name'"}), 400

    row = fetch_one(
        "UPDATE users SET name = %s WHERE id = %s RETURNING id, name;",
        (name, user_id)
    )

    if not row:
        return jsonify({"error": "Usuari no trobat"}), 404

    return jsonify({"id": row[0], "name": row[1]})


@app.post("/api/users")
def create_user():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()

    if not name:
        return jsonify({"error": "Falta 'name'"}), 400

    row = fetch_one(
        "INSERT INTO users (name) VALUES (%s) RETURNING id, name;",
        (name,)
    )

    return jsonify({"id": row[0], "name": row[1]}), 201

if __name__ == "__main__":
    app.run(debug=True)
