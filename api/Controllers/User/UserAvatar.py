from flask import jsonify, Blueprint, request
import os
import re
import requests
from uuid import uuid4
from urllib.parse import urlparse
from api.Models.Base import SessionLocal
from api.Services.UserService import UserService

user_avatar_bp = Blueprint("user_avatar", __name__)

BLOB_READ_WRITE_TOKEN = os.getenv("BLOB_READ_WRITE_TOKEN", "")
ALLOWED_EXTENSIONS = {"jpeg", "jpg", "png", "webp", "gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def delete_blob_by_url(blob_url):
    if not blob_url or not BLOB_READ_WRITE_TOKEN:
        return False

    try:
        parsed = urlparse(blob_url)
        blob_path = parsed.path.lstrip("/")
        if not blob_path:
            return False

        delete_url = f"https://blob.vercel-storage.com/{blob_path}"
        headers = {
            "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}"
        }

        response = requests.delete(delete_url, headers=headers, timeout=20)
        return response.status_code in [200, 202, 204, 404]
    except Exception:
        return False


@user_avatar_bp.post("/api/users/<int:user_id>/avatar")
def upload_avatar(user_id):
    """
    Upload avatar image to Vercel Blob and save URL to user record using SQLAlchemy.
    """
    db = SessionLocal()
    try:
        user = UserService.get_by_id(db, user_id)
        if not user:
            return jsonify({"error": "Usuari no trobat"}), 404

        old_avatar_url = user.avatar
        username = user.username or f"user{user_id}"
        safe_username = re.sub(r'[^a-zA-Z0-9_-]', '', username) or f"user{user_id}"
        
        if "file" not in request.files:
            return jsonify({"error": "Falta el camp 'file'"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Cap fitxer seleccionat"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Format de fitxer no permés (JPEG/PNG/WEBP/GIF)"}), 400
        
        file_bytes = file.read()
        if len(file_bytes) > MAX_FILE_SIZE:
            return jsonify({"error": f"Fitxer massa gran (màxim {MAX_FILE_SIZE / 1024 / 1024}MB)"}), 400
        
        if not BLOB_READ_WRITE_TOKEN:
            return jsonify({"error": "Vercel Blob no configurat al servidor"}), 500
        
        original_filename = file.filename or ""
        file_ext = original_filename.rsplit(".", 1)[1].lower() if "." in original_filename else "jpg"
        blob_filename = f"avatars/{safe_username}_{uuid4().hex[:8]}.{file_ext}"
        
        upload_url = f"https://blob.vercel-storage.com/{blob_filename}"
        headers = {
            "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
            "x-add-random-suffix": "0",
            "x-upsert": "true"
        }
        
        response = requests.put(
            upload_url,
            headers=headers,
            data=file_bytes,
            params={"filename": blob_filename},
            timeout=30
        )
        
        if response.status_code not in [200, 201]:
            return jsonify({"error": f"Error pujant a Vercel Blob: HTTP {response.status_code}"}), 500
        
        try:
            response_data = response.json()
            blob_url = response_data.get("url", "")
        except:
            blob_url = ""
        
        if not blob_url:
            return jsonify({"error": "No s'ha rebut URL de Vercel Blob"}), 500
        
        # Save blob URL via SQlAlchemy Service
        UserService.update(db, user_id, {"avatar": blob_url})

        if old_avatar_url and old_avatar_url != blob_url:
            delete_blob_by_url(old_avatar_url)
        
        return jsonify({
            "avatar_url": blob_url,
            "message": "Avatar actualitzat correctament"
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Error pujant fitxer: {str(e)}"}), 500
    finally:
        db.close()


@user_avatar_bp.delete("/api/users/<int:user_id>/avatar")
def delete_avatar(user_id):
    """
    Remove user avatar URL from DB using SQLAlchemy.
    """
    db = SessionLocal()
    try:
        user = UserService.get_by_id(db, user_id)
        if not user:
            return jsonify({"error": "Usuari no trobat"}), 404

        current_avatar_url = user.avatar
        blob_deleted = False

        if current_avatar_url:
            blob_deleted = delete_blob_by_url(current_avatar_url)

        UserService.update(db, user_id, {"avatar": None})

        return jsonify({
            "message": "Avatar eliminat correctament",
            "blob_deleted": blob_deleted
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error eliminant avatar: {str(e)}"}), 500
    finally:
        db.close()
