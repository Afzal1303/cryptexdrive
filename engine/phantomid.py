import jwt
import datetime
import uuid
from config import SECRET_KEY

def generate_dynamic_id(username):
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "user": username,
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + datetime.timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_dynamic_id(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user"]
    except:
        return None
