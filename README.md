# CryptexDrive 💎

CryptexDrive is a high-security cloud file sharing platform designed with a "No Permanent Sessions" philosophy. It combines multi-step verification, short-lived stateless authorization (Dynamic ID), and AES-256 encryption at rest to ensure maximum data protection and user isolation.

## 🛡️ Core Security Principles

- **No Permanent Sessions:** Short-lived JWTs stored in `sessionStorage` are validated on every request.
- **Dynamic ID:** Every authorized session is tied to a unique, time-limited Dynamic ID.
- **Stateless Encryption:** Files are encrypted/decrypted in-memory using AES-256; storage providers never see plaintext data.
- **Multi-Factor Auth:** Password authentication is layered with mandatory email-based OTP verification.
- **Zero-Trust Logic:** No direct file access is possible without a valid, verified Dynamic ID.

## ✨ Key Features

- **Hybrid Cloud Storage:** Seamlessly switch between local storage and S3-compatible providers (AWS/DigitalOcean).
- **AI-Assisted Security:** Cryptex AI Engine analyzes file metadata during upload to calculate risk scores and detect anomalies.
- **Self-Healing:** Automated quarantine of high-risk files (Risk Score > 80).
- **Admin Dashboard:** Real-time audit logging and system health monitoring for administrators.
- **Token Blacklisting:** Immediate revocation of compromised tokens with Redis support.
- **Modern UI:** Responsive Glassmorphism interface for a premium security experience.

## 🛠️ Technology Stack

- **Backend:** Flask (Python)
- **Database:** SQLite (Default) / PostgreSQL (Production)
- **Security:** PyJWT, Cryptography (AES-256), Werkzeug (PBKDF2)
- **Cloud:** Boto3 (Hybrid S3 Interface)
- **Infrastructure:** Gunicorn, Redis (Optional for Blacklisting)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Gmail account (for OTP delivery)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/CryptexDrive.git
   cd CryptexDrive
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   Copy `.env.example` to `.env` and configure your settings:
   ```bash
   cp .env.example .env
   ```
   *Required fields: `SECRET_KEY`, `MAIL_USERNAME`, `MAIL_PASSWORD`.*

5. **Initialize Database & Start Application:**
   ```bash
   # Start the main application
   python app/app.py
   ```

### 🔐 Administrative Setup

To access the admin portal (`/admin/dashboard`):

1. **Create an admin user:**
   ```bash
   python admin/create_admin.py
   ```
2. **Launch the admin gateway:**
   ```bash
   python app/admin_app.py
   ```

## 📁 Project Structure

- `app/`: Primary application backends (`app.py`, `admin_app.py`).
- `engine/`: Core authentication, JWT (PhantomID), and blacklisting logic.
- `improvise/`: Security enhancements (AI Analyzer, Audit Logs, Vault Encryption, Self-Healing).
- `cloud/`: SkyStore hybrid storage abstraction.
- `static/` & `templates/`: Frontend assets and UI templates.
- `docs/`: Technical documentation and project roadmap.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
