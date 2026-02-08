import jwt
from functools import wraps
from flask import request, session
from config import SECRET_KEY
from .blacklist import is_jti_blacklisted
from .gatekeeper import is_admin

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        # 1️⃣ Try Authorization header
        auth = request.headers.get("Authorization")
        if auth:
            if auth.startswith("Bearer "):
                token = auth[7:]
            else:
                token = auth

        # 2️⃣ Fallback to session (Required for direct page navigation)
        if not token:
            token = session.get("dynamic_id")

        if not token or not isinstance(token, str) or len(token) < 10:
            return {"error": "valid token missing"}, 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = payload["user"]
            jti = payload.get("jti")

            # 🛑 Check Redis Blacklist
            if jti and is_jti_blacklisted(jti):
                return {"error": "token has been blacklisted (Intrusion Detected)"}, 401

        except jwt.ExpiredSignatureError:
            return {"error": "token expired"}, 401
        except jwt.InvalidTokenError:
            return {"error": "invalid token"}, 401

        return f(user, *args, **kwargs)

    return decorated

def admin_required(f):
    @wraps(f)
    @jwt_required
    def decorated(user, *args, **kwargs):
        if not is_admin(user):
            return {"error": "admin access required"}, 403
        return f(user, *args, **kwargs)
    return decorated
