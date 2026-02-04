import jwt
from functools import wraps
from flask import request, session
from config import SECRET_KEY

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        # 1️⃣ Try Authorization header
        auth = request.headers.get("Authorization")
        if auth:
            token = auth.replace("Bearer ", "")

        # 2️⃣ Fallback to session (AUTO)
        if not token:
            token = session.get("dynamic_id")

        if not token:
            return {"error": "token missing"}, 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = payload["user"]
        except jwt.ExpiredSignatureError:
            return {"error": "token expired"}, 401
        except jwt.InvalidTokenError:
            return {"error": "invalid token"}, 401

        return f(user, *args, **kwargs)

    return decorated
