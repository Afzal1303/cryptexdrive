from functools import wraps
from flask import request
from engine.phantomid import verify_dynamic_id

def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return {"error": "missing token"}, 401

        # Expect: Bearer <token>
        if not auth_header.startswith("Bearer "):
            return {"error": "invalid token format"}, 401

        token = auth_header.split(" ")[1]

        user = verify_dynamic_id(token)
        if not user:
            return {"error": "invalid or expired token"}, 401

        return func(user, *args, **kwargs)

    return wrapper
