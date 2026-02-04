from flask import Flask, request, session, send_from_directory, render_template
from flask_mail import Mail, Message
import os

from config import *
from engine.gatekeeper import (
    init_users,
    verify_user,
    generate_otp,
    verify_otp,
    register_user,
    get_email
)
from engine.phantomid import generate_dynamic_id
from engine.auth import jwt_required

app = Flask(__name__)
app.secret_key = SECRET_KEY

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =====================
# MAIL CONFIG
# =====================
app.config.update(
    MAIL_SERVER=MAIL_SERVER,
    MAIL_PORT=MAIL_PORT,
    MAIL_USE_TLS=MAIL_USE_TLS,
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
)

mail = Mail(app)
init_users()

# =====================
# INDEX
# =====================
@app.route("/")
def index():
    return render_template("index.html")


# =====================
# REGISTER
# =====================
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if register_user(data["username"], data["password"], data["email"]):
        return {"status": "registered"}
    return {"error": "registration failed (username taken?)"}, 400


# =====================
# LOGIN (PASSWORD)
# =====================
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    if verify_user(data["username"], data["password"]):
        session.clear()
        session["user"] = data["username"]
        session["auth"] = "password_ok"
        return {"status": "password ok"}

    return {"error": "invalid credentials"}, 401


# =====================
# SEND OTP
# =====================
@app.route("/send-otp", methods=["POST"])
def send_otp():
    if session.get("auth") != "password_ok":
        return {"error": "unauthorized"}, 401

    otp = generate_otp(session["user"])
    if otp is None:
        return {"error": "wait before requesting otp"}, 429

    email = get_email(session["user"])
    if not email:
        return {"error": "user email not found"}, 400

    msg = Message(
        "CryptexDrive OTP",
        sender=MAIL_USERNAME,
        recipients=[email]
    )
    msg.body = f"Your CryptexDrive OTP is: {otp}"
    
    try:
        mail.send(msg)
        return {"status": "otp sent"}
    except Exception as e:
        print(f"Mail Error: {e}")
        return {"error": f"Failed to send email: {str(e)}"}, 500


# =====================
# VERIFY OTP + GENERATE DYNAMIC ID
# =====================
@app.route("/verify-otp", methods=["POST"])
def verify():
    data = request.json

    if verify_otp(data["username"], data["otp"]):
        token = generate_dynamic_id(data["username"])

        # 🔐 STORE TOKEN IN SESSION
        session["dynamic_id"] = token
        session["auth"] = "2fa_ok"

        return {
            "status": "2FA success",
            "dynamic_id": token
        }

    return {"error": "invalid otp"}, 401


# =====================
# PROTECTED CHECK
# =====================
@app.route("/secure", methods=["GET"])
@jwt_required
def secure(user):
    return {
        "status": "authorized",
        "user": user
    }


# =====================
# FILE UPLOAD
# =====================
@app.route("/upload", methods=["POST"])
@jwt_required
def upload(user):
    if "file" not in request.files:
        return {"error": "no file"}, 400

    file = request.files["file"]
    user_dir = os.path.join(UPLOAD_FOLDER, user)
    os.makedirs(user_dir, exist_ok=True)

    file.save(os.path.join(user_dir, file.filename))

    return {"status": "uploaded", "file": file.filename}


# =====================
# LIST FILES
# =====================
@app.route("/files", methods=["GET"])
@jwt_required
def files(user):
    user_dir = os.path.join(UPLOAD_FOLDER, user)
    if not os.path.exists(user_dir):
        return {"files": []}

    return {"files": os.listdir(user_dir)}


# =====================
# DOWNLOAD FILE
# =====================
@app.route("/download/<filename>")
@jwt_required
def download(user, filename):
    return send_from_directory(
        os.path.join(UPLOAD_FOLDER, user),
        filename,
        as_attachment=True
    )


# =====================
# RUN
# =====================
if __name__ == "__main__":
    app.run(debug=True)
