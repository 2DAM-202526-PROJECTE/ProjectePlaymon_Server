from flask import jsonify, Blueprint, request
import os
import requests
from db import fetch_one

user_avatar_bp = Blueprint("user_avatar", __name__)

IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID", "")
IMGUR_API_URL = "https://api.imgur.com/3/image"
ALLOWED_EXTENSIONS = {"jpeg", "jpg", "png", "webp", "gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@user_avatar_bp.post("/api/users/<int:user_id>/avatar")
def upload_avatar(user_id):
    """
    Upload avatar image to imgur and save URL to user record.
    
    Expects multipart form with 'file' field.
    Returns: { "avatar_url": "https://imgur.com/..." }
    """
    
    # Check if user exists (security: user can only upload for themselves in production)
    user_row = fetch_one("SELECT id FROM users WHERE id = %s", (user_id,))
    if not user_row:
        return jsonify({"error": "Usuari no trobat"}), 404
    
    # Validate file
    if "file" not in request.files:
        return jsonify({"error": "Falta el camp 'file'"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Cap fitxer seleccionat"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Format de fitxer no permés (JPEG/PNG/WEBP/GIF)"}), 400
    
    # Check file size
    file_size = len(file.read())
    file.seek(0)  # Reset file pointer
    if file_size > MAX_FILE_SIZE:
        return jsonify({"error": f"Fitxer massa gran (màxim {MAX_FILE_SIZE / 1024 / 1024}MB)"}), 400
    
    # Upload to imgur
    try:
        if not IMGUR_CLIENT_ID:
            return jsonify({"error": "Imgur no configurat al servidor"}), 500
        
        headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
        files = {"image": file.stream}
        
        response = requests.post(IMGUR_API_URL, headers=headers, files=files, timeout=10)
        
        if response.status_code != 200:
            error_msg = response.json().get("data", {}).get("error", "Unknown error")
            return jsonify({"error": f"Error uploading to imgur: {error_msg}"}), 500
        
        imgur_data = response.json().get("data", {})
        imgur_url = imgur_data.get("link", "")
        
        if not imgur_url:
            return jsonify({"error": "No s'ha rebut URL de Imgur"}), 500
        
        # Save imgur URL to database
        try:
            fetch_one(
                "UPDATE users SET avatar = %s WHERE id = %s RETURNING id",
                (imgur_url, user_id)
            )
        except Exception as e:
            return jsonify({"error": f"Error guardant a la BD: {str(e)}"}), 500
        
        return jsonify({
            "avatar_url": imgur_url,
            "message": "Avatar actualitzat correctament"
        }), 200
    
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error comunicant amb imgur: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error desconegut: {str(e)}"}), 500
