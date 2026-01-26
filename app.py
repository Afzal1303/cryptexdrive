from flask import (
    Flask, request, session,
    send_from_directory, render_template
)
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
from engine.vaultcore import (
    save_file,
    list_files,
    file_path
)

# =====================
# APP SETUP
# =====================
app = Flask(__name__)
app.secret_key = SECRET_KEY

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
# FRONTEND
# =====================
@app.route("/")
def home():
    return render_template("index.html")

# =====================
# AUTH
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
# SECURE AREA
# =====================
@app.route("/secure", methods=["GET"])
@jwt_required
def secure(user):
    return {"status": "authorized", "user": user}

# =====================
# FILE VAULT
# =====================
@app.route("/upload", methods=["POST"])
@jwt_required
def upload(user):
    if "file" not in request.files:
        return {"error": "no file provided"}, 400

    file = request.files["file"]
    filename = save_file(user, file)

    return {"status": "uploaded", "file": filename}


@app.route("/files", methods=["GET"])
@jwt_required
def files(user):
    return {"files": list_files(user)}


@app.route("/download/<filename>", methods=["GET"])
@jwt_required
def download(user, filename):
    directory = os.path.dirname(file_path(user, filename))
    return send_from_directory(directory, filename, as_attachment=True)

# =====================
# RUN
# =====================
if __name__ == "__main__":
    app.run(debug=True)
