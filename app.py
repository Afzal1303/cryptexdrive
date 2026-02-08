from flask import Flask, request, session, send_from_directory, render_template, Response, redirect, url_for
from flask_mail import Mail, Message
import jwt
import os
import io
import re
import shutil

from config import *
from engine.gatekeeper import (
    init_users,
    verify_user,
    generate_otp,
    verify_otp,
    register_user,
    get_email,
    is_admin,
    delete_user_db
)
from engine.phantomid import generate_dynamic_id
from engine.auth import jwt_required, admin_required

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
# ADMIN DASHBOARD & LOGIN
# =====================
@app.route("/admin/login")
def admin_login_page():
    return render_template("admin_login.html")

@app.route("/api/admin/login", methods=["POST"])
def admin_login_api():
    data = request.json
    if not data or not all(k in data for k in ("username", "password")):
        return {"error": "missing credentials"}, 400

    username = data["username"]
    if verify_user(username, data["password"]):
        if not is_admin(username):
            AuditLogger.log_event(username, "admin_login_attempt", "failed:not_admin")
            return {"error": "Access Denied: Not an administrator"}, 403
            
        session.clear()
        session["user"] = username
        session["auth"] = "password_ok"
        AuditLogger.log_event(username, "admin_login_password", "success")
        return {"status": "password ok"}

    AuditLogger.log_event(data.get("username", "unknown"), "admin_login_password", "failed")
    return {"error": "invalid credentials"}, 401

@app.route("/admin/dashboard")
def admin_dashboard_page():
    token = session.get("dynamic_id")
    if not token:
        return redirect(url_for("admin_login_page"))

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = payload["user"]
        if not is_admin(user):
            AuditLogger.log_event(user, "admin_dashboard_access", "denied:not_admin")
            return "Access Denied", 403
        return render_template("admin.html")
    except Exception:
        return redirect(url_for("admin_login_page"))

@app.route("/api/admin/logs")
@admin_required
def get_admin_logs(user):
    logs = AuditLogger.get_all_logs()
    return {"logs": logs}

@app.route("/api/admin/stats")
@admin_required
def get_admin_stats(user):
    from improvise.db import get_db_context
    stats = {}
    
    with get_db_context() as db:
        # Total Users
        stats["total_users"] = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        
        # Total Files
        stats["total_files"] = db.execute("SELECT COUNT(*) FROM file_metadata").fetchone()[0]
        
        # Average Risk Score
        avg_risk = db.execute("SELECT AVG(risk_score) FROM file_metadata").fetchone()[0]
        stats["avg_risk"] = round(avg_risk, 1) if avg_risk else 0
        
        # Quarantined Files
        stats["quarantined"] = db.execute("SELECT COUNT(*) FROM file_metadata WHERE is_active=0").fetchone()[0]
        
        # Risk Distribution (Safe, Warning, Critical)
        stats["risk_dist"] = {
            "safe": db.execute("SELECT COUNT(*) FROM file_metadata WHERE risk_score < 50").fetchone()[0],
            "warning": db.execute("SELECT COUNT(*) FROM file_metadata WHERE risk_score >= 50 AND risk_score < 80").fetchone()[0],
            "critical": db.execute("SELECT COUNT(*) FROM file_metadata WHERE risk_score >= 80").fetchone()[0]
        }
        
    return stats


# =====================
# REGISTER
# =====================
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if not data or not all(k in data for k in ("username", "password", "email")):
        return {"error": "missing required fields"}, 400
    
    username = data["username"]
    if not username or not data["password"] or not data["email"]:
        return {"error": "fields cannot be empty"}, 400

    # 🛡️ SANITIZE USERNAME
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return {"error": "invalid username (only alphanumeric and underscores allowed)"}, 400

    success = register_user(username, data["password"], data["email"])
    
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
    if not data or not all(k in data for k in ("username", "password")):
        return {"error": "missing credentials"}, 400

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
    if session.get("auth") != "password_ok":
        return {"error": "unauthorized session state"}, 401

    data = request.json
    if not data or "otp" not in data:
        return {"error": "otp required"}, 400

    username = session.get("user") or data.get("username")

    if not username:
        return {"error": "username missing"}, 400

    if verify_otp(username, data.get("otp")):
        token = generate_dynamic_id(username)

        # 🔐 STORE TOKEN IN SESSION
        session["dynamic_id"] = token
        session["auth"] = "2fa_ok"

        is_user_admin = is_admin(username)

        AuditLogger.log_event(username, "verify_otp", "success")
        return {
            "status": "2FA success",
            "dynamic_id": token,
            "is_admin": is_user_admin
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
    
    # 🛡️ IMMEDIATE SELF-HEALING: If risk is extreme, blacklist the token immediately
    if analysis["risk_score"] >= 90:
        token = request.headers.get("Authorization") or session.get("dynamic_id")
        SecurityHarden.detect_intrusion_and_blacklist(token, "Extreme Risk File Upload")
    
    # 3. Encryption at Rest
    try:
        Vault.encrypt_file(file_path)
    except Exception as e:
        AuditLogger.log_event(user, f"upload:{filename}", f"failed:encryption_error:{str(e)}")
        return {"error": "failed to secure file"}, 500
    
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

    # Filter out .quarantine files
    all_files = os.listdir(user_dir)
    safe_files = [f for f in all_files if not f.endswith(".quarantine")]
    return {"files": safe_files}


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
# DELETE ACCOUNT
# =====================
@app.route("/delete-account", methods=["POST"])
@jwt_required
def delete_account(user):
    data = request.json
    if not data or "password" not in data:
        return {"error": "password required to delete account"}, 400

    # 1. Verify Password
    if not verify_user(user, data["password"]):
        AuditLogger.log_event(user, "delete_account", "failed:invalid_password")
        return {"error": "invalid password"}, 401

    # 2. Delete Files from Disk
    user_dir = os.path.join(UPLOAD_FOLDER, user)
    if os.path.exists(user_dir):
        try:
            shutil.rmtree(user_dir)
        except Exception as e:
            print(f"Error deleting user directory: {e}")

    # 3. Delete Metadata from DB
    from improvise.db import get_db_context
    try:
        with get_db_context() as db:
            db.execute("DELETE FROM file_metadata WHERE owner = ?", (user,))
    except Exception as e:
        print(f"Error deleting metadata: {e}")

    # 4. Delete User from DB
    if delete_user_db(user):
        AuditLogger.log_event(user, "delete_account", "success")
        session.clear()
        return {"status": "account deleted successfully"}
    
    return {"error": "failed to delete account record"}, 500


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
