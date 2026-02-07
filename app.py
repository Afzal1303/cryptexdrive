from flask import Flask, request, session, send_from_directory, render_template, Response
from flask_mail import Mail, Message
import os
import io

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

# 🚀 IMPROVISE IMPORTS
from improvise import (
    bootstrap_improvements,
    Vault,
    AIAnalyzer,
    AuditLogger,
    SecurityHarden
)

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

# =====================
# INITIALIZE SYSTEM
# =====================
init_users()
bootstrap_improvements()

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
    success = register_user(data["username"], data["password"], data["email"])
    
    if success:
        AuditLogger.log_event(data["username"], "register", "success")
        return {"status": "registered"}
    
    AuditLogger.log_event(data.get("username", "unknown"), "register", "failed")
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
        AuditLogger.log_event(data["username"], "login_password", "success")
        return {"status": "password ok"}

    AuditLogger.log_event(data.get("username", "unknown"), "login_password", "failed")
    return {"error": "invalid credentials"}, 401


# =====================
# SEND OTP
# =====================
@app.route("/send-otp", methods=["POST"])
def send_otp():
    if session.get("auth") != "password_ok":
        return {"error": "unauthorized"}, 401

    user = session["user"]
    otp = generate_otp(user)
    if otp is None:
        AuditLogger.log_event(user, "send_otp", "rate_limited")
        return {"error": "wait before requesting otp"}, 429

    email = get_email(user)
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
        AuditLogger.log_event(user, "send_otp", "success")
        return {"status": "otp sent"}
    except Exception as e:
        print(f"Mail Error: {e}")
        AuditLogger.log_event(user, "send_otp", "failed")
        return {"error": f"Failed to send email: {str(e)}"}, 500


# =====================
# VERIFY OTP + GENERATE DYNAMIC ID
# =====================
@app.route("/verify-otp", methods=["POST"])
def verify():
    data = request.json
    username = data.get("username")

    if verify_otp(username, data["otp"]):
        token = generate_dynamic_id(username)

        # 🔐 STORE TOKEN IN SESSION
        session["dynamic_id"] = token
        session["auth"] = "2fa_ok"

        AuditLogger.log_event(username, "verify_otp", "success")
        return {
            "status": "2FA success",
            "dynamic_id": token
        }

    AuditLogger.log_event(username, "verify_otp", "failed")
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
# FILE UPLOAD (IMPROVISED)
# =====================
@app.route("/upload", methods=["POST"])
@jwt_required
def upload(user):
    if "file" not in request.files:
        return {"error": "no file"}, 400

    file = request.files["file"]
    
    # 1. Sanitize filename
    filename = SecurityHarden.sanitize_path(file.filename)
    
    user_dir = os.path.join(UPLOAD_FOLDER, user)
    os.makedirs(user_dir, exist_ok=True)
    
    file_path = os.path.join(user_dir, filename)
    file.save(file_path)

    # 2. AI Analysis
    analysis = AIAnalyzer.analyze_file(file_path, filename, user)
    
    # 3. Encryption at Rest
    Vault.encrypt_file(file_path)
    
    # 4. Audit Log
    AuditLogger.log_event(user, f"upload:{filename}", "success")

    return {
        "status": "uploaded", 
        "file": filename,
        "ai_analysis": analysis
    }


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
# DOWNLOAD FILE (IMPROVISED)
# =====================
@app.route("/download/<filename>")
@jwt_required
def download(user, filename):
    # Sanitize input
    filename = SecurityHarden.sanitize_path(filename)
    file_path = os.path.join(UPLOAD_FOLDER, user, filename)
    
    if not os.path.exists(file_path):
        AuditLogger.log_event(user, f"download:{filename}", "failed:not_found")
        return {"error": "file not found"}, 404

    try:
        # Decrypt in memory for safe delivery
        decrypted_data = Vault.decrypt_file_data(file_path)
        
        AuditLogger.log_event(user, f"download:{filename}", "success")
        
        return Response(
            io.BytesIO(decrypted_data),
            mimetype="application/octet-stream",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
    except Exception as e:
        AuditLogger.log_event(user, f"download:{filename}", f"failed:{str(e)}")
        return {"error": "decryption failed"}, 500


# =====================
# LOGOUT
# =====================
@app.route("/logout", methods=["POST"])
def logout():
    user = session.get("user", "unknown")
    session.clear()
    AuditLogger.log_event(user, "logout", "success")
    return {"status": "logged out"}


# =====================
# RUN
# =====================
if __name__ == "__main__":
    app.run(debug=True)