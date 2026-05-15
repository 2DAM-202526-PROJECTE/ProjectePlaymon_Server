import jwt
import os
from flask import request as flask_request

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"


def decode_jwt(req=None):
    """Returns (payload, error_tuple). error_tuple is (dict, status_code) or None."""
    if req is None:
        req = flask_request
    auth_header = req.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, ({"error": "Token no proporcionat"}, 401)
    token = auth_header[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, ({"error": "Token expirat"}, 401)
    except jwt.InvalidTokenError:
        return None, ({"error": "Token invàlid"}, 401)


def require_admin(req=None):
    """Returns (payload, error_tuple). error_tuple set if not admin."""
    payload, err = decode_jwt(req)
    if err:
        return None, err
    if payload.get("role") != "admin":
        return None, ({"error": "Accés restringit a administradors"}, 403)
    return payload, None
