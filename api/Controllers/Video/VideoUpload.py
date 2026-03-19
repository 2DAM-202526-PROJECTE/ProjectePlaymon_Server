from flask import jsonify, Blueprint, request
import os
import re
from uuid import uuid4
from api.Models.Base import SessionLocal
from api.Services.UserService import UserService
from api.Services.VideoService import VideoService

# Cloudinary setup
cloudinary_url = (os.getenv("CLOUDINARY_URL") or "").strip()
cloudinary_config_error = None

if cloudinary_url and not cloudinary_url.startswith("cloudinary://"):
    cloudinary_config_error = "Invalid CLOUDINARY_URL format"
    os.environ.pop("CLOUDINARY_URL", None)
    cloudinary_url = ""

import cloudinary
import cloudinary.uploader

video_upload_bp = Blueprint("video_upload", __name__)

if cloudinary_url:
    try:
        cloudinary.config(cloudinary_url=cloudinary_url)
    except Exception as e:
        cloudinary_config_error = str(e)
        cloudinary_url = ""

ALLOWED_EXTENSIONS = {"mp4", "webm", "ogg", "mov", "avi", "mkv", "flv", "wmv"}
MAX_FILE_SIZE = 500 * 1024 * 1024


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@video_upload_bp.post("/api/videos/upload")
def upload_video():
    user_id = request.headers.get("X-User-ID") or request.form.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid user_id"}), 400

    db = SessionLocal()
    try:
        user = UserService.get_by_id(db, user_id)
        if not user:
            return jsonify({"error": "Usuari no trobat"}), 404

        if "file" not in request.files:
            return jsonify({"error": "Falta el camp 'file'"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Cap fitxer seleccionat"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Format de vídeo no permés"}), 400

        file_bytes = file.read()
        file_size = len(file_bytes)
        if file_size > MAX_FILE_SIZE:
             return jsonify({"error": "Vídeo massa gran"}), 400

        title = (request.form.get("title") or "Sin título").strip()
        description = (request.form.get("description") or "").strip()
        is_public = request.form.get("is_public", "false").lower() in ("true", "1", "yes")

        if not cloudinary_url or cloudinary_config_error:
            return jsonify({"error": "Cloudinary no disponible"}), 500

        unique_id = uuid4().hex[:8]
        safe_username = re.sub(r'[^a-zA-Z0-9_-]', '', user.username or f"user{user_id}")
        public_id = f"playmon/{safe_username}/{unique_id}"

        file.seek(0)
        upload_result = cloudinary.uploader.upload(
            file,
            resource_type="video",
            public_id=public_id,
            folder="playmon"
        )
        
        video_url = upload_result.get("secure_url")
        if not video_url:
            return jsonify({"error": "Error Cloudinary upload"}), 500

        video = VideoService.create(db, {
            "user_id": user_id,
            "title": title,
            "description": description,
            "video_url": video_url,
            "file_size": file_size,
            "is_public": is_public
        })

        return jsonify(video.to_dict()), 201

    except Exception as e:
        return jsonify({"error": f"Error pujant vídeo: {str(e)}"}), 500
    finally:
        db.close()

@video_upload_bp.get("/api/videos")
def get_videos():
    user_id = request.args.get("user_id")
    limit = min(int(request.args.get("limit", 20)), 100)
    offset = int(request.args.get("offset", 0))
    
    db = SessionLocal()
    try:
        if user_id:
             videos = VideoService.get_user_videos(db, int(user_id), limit, offset)
        else:
             videos = VideoService.get_public_videos(db, limit, offset)
        
        return jsonify({"videos": [v.to_dict() for v in videos]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@video_upload_bp.get("/api/videos/<int:video_id>")
def get_video(video_id):
    db = SessionLocal()
    try:
        video = VideoService.get_by_id(db, video_id)
        if not video:
            return jsonify({"error": "Vídeo no trobat"}), 404
        return jsonify(video.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@video_upload_bp.delete("/api/videos/<int:video_id>")
def delete_video(video_id):
    db = SessionLocal()
    try:
        success = VideoService.delete(db, video_id)
        if success:
             return jsonify({"message": "Vídeo eliminat correctament"}), 200
        return jsonify({"error": "Vídeo no trobat"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
