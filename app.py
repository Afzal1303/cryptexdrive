from flask import Flask, request, session, send_from_directory
from flask_mail import Mail, Message
import os

from config import *
from engine.gatekeeper import (
    init_users,
    verify_user,
    generate_otp,
    verify_otp
)
from engine.phantomid import generate_dynamic_id
from engine.auth import jwt_required

# =====================
# APP SETUP
# =====================
app = Flask(__name__)
app.secret_key = SECRET_KEY

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
# AUTH ROUTES
# =====================

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if verify_user(data["username"], data["password"]):
        session["user"] = data["username"]
        return {"status": "password ok"}
    return {"error": "invalid credentials"}, 401


@app.route("/send-otp", methods=["POST"])
def send_otp():
    if "user" not in session:
        return {"error": "unauthorized"}, 401

    otp = generate_otp(session["user"])
    if otp is None:
        return {"error": "wait before requesting otp"}, 429

    email = request.json["email"]
    msg = Message(
        "CryptexDrive OTP",
        sender=MAIL_USERNAME,
        recipients=[email]
    )
    msg.body = f"Your CryptexDrive OTP is: {otp}"
    mail.send(msg)

    return {"status": "otp sent"}


@app.route("/verify-otp", methods=["POST"])
def verify():
    data = request.json
    if verify_otp(data["username"], data["otp"]):
        token = generate_dynamic_id(data["username"])
        return {"dynamic_id": token}
    return {"error": "invalid otp"}, 401


# =====================
# PROTECTED ROUTES
# =====================

@app.route("/secure", methods=["GET"])
@jwt_required
def secure(user):
    return {"status": "authorized", "user": user}


@app.route("/upload", methods=["POST"])
@jwt_required
def upload(user):
    if "file" not in request.files:
        return {"error": "no file"}, 400

    file = request.files["file"]
    user_dir = os.path.join(UPLOAD_FOLDER, user)
    os.makedirs(user_dir, exist_ok=True)

    path = os.path.join(user_dir, file.filename)
    file.save(path)

    return {"status": "uploaded", "file": file.filename}


@app.route("/files", methods=["GET"])
@jwt_required
def files(user):
    user_dir = os.path.join(UPLOAD_FOLDER, user)
    if not os.path.exists(user_dir):
        return {"files": []}
    return {"files": os.listdir(user_dir)}


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

from flask import render_template

@app.route("/")
def home():
    return render_template("index.html")
