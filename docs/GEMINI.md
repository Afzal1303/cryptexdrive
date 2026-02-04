CryptexDrive – Project Context, Progress & Operational Rules

This document defines the current implementation state, design decisions, progress tracking, and AI operational rules for the CryptexDrive project.

It serves as the single source of truth for:

Development clarity

Academic / review explanation

Future scalability planning

1. Project Overview

Project Name: CryptexDrive
Domain: Secure Cloud File Sharing
Architecture Style: Modular Backend with Token-Based Authorization
Backend Type: API-driven (stateless authorization)

Primary Objective

CryptexDrive aims to provide a secure file storage and sharing system that ensures:

Strong user authentication

Multi-step verification

Short-lived authorization tokens

Strict access isolation between users

The system is designed to avoid permanent sessions, reduce attack surface, and prevent unauthorized file access.

2. Core Security Principles

The entire project is built around these principles:

No plaintext password storage

No permanent login sessions

No direct file access without authorization

No trust without verification

Short-lived identity instead of long-lived sessions

3. Technology Stack
Backend Stack

Python (Flask)

SQLite (local persistence)

Flask-Mail (Gmail SMTP)

Werkzeug Security (password hashing)

PyJWT (Dynamic ID generation)

Security Components

Password hashing (PBKDF2)

Email-based OTP verification

Time-limited JWT tokens (Dynamic ID)

Decorator-based authorization

User-isolated file storage

4. Authentication & Authorization Flow (Verified)

The authentication system follows a layered verification approach.

Step-by-Step Flow

User Login
→ Username & Password Validation
→ OTP Generated & Sent to Gmail
→ OTP Verification
→ Dynamic ID (JWT) Issued
→ Authorized Access to Secure APIs

Why This Flow Is Used

Password alone is insufficient

OTP ensures email ownership

Dynamic ID ensures short-term authorization

Middleware prevents unauthorized access

5. Password Authentication Module
Functionality

Passwords are hashed using Werkzeug

No plaintext passwords stored

Hash comparison during login

Security Outcome

Database compromise does not expose passwords

Replay attacks are prevented

6. OTP Verification Module (Stable & Working)
OTP Characteristics

Random numeric OTP

Time-limited validity

Sent only via registered email

Protection Mechanisms

OTP expires automatically

Rate-limited generation

Stored temporarily in database

Verified before Dynamic ID issuance

7. Dynamic ID (JWT) Design & Purpose
What Is Dynamic ID

The Dynamic ID is a JWT token that represents a verified user identity for a short duration.

It replaces traditional long-term sessions.

Why Dynamic ID Is Used

Prevents session hijacking

Automatically expires

Stateless verification

No server-side session storage required

Token Properties

Algorithm: HS256

Payload includes:

Username

Issued time (iat)

Expiry time (exp)

Lifetime: Short-lived (minutes)

Usage Pattern

Generated only after OTP verification

Sent via HTTP Authorization header

Validated on every protected route

8. Authorization Middleware (JWT Guard)
Role of Middleware

Intercepts protected API requests

Validates Dynamic ID

Rejects expired or invalid tokens

Injects verified user identity into request

Security Impact

Unauthorized access blocked centrally

No route bypass possible

Consistent enforcement across APIs

9. File Handling Module (Current Implementation)
Supported Operations

File upload

File listing

File download

Storage Strategy

Files stored on server filesystem

Each user has a dedicated directory

Directory name derived from verified user

No shared storage between users

Access Control

File operations require valid Dynamic ID

Users cannot access other users’ files

Middleware enforces ownership

10. Project Progress Status
✅ Completed Phases

User registration & login

Password hashing & verification

Gmail-based OTP system

OTP expiration & validation

Dynamic ID (JWT) generation

Authorization middleware

Secure file upload

File listing & download logic

Frontend integration

⏳ Pending Phases

AI-assisted file analysis

Cloud Deployment (AWS / Render / Railway)

Secure audit logging

File encryption at rest

Access activity tracking

11. AI Engine – Operational Rules (Approved)

⚠️ AI Engine is not implemented yet.
This section defines strict rules that the AI must follow once added.

AI Engine Scope

The AI engine will:

Analyze file metadata

Detect potential risks

Suggest improvements

The AI engine will not enforce actions.

AI Operational Rules

AI must never modify files automatically

AI must only analyze and suggest

AI must operate on metadata only

AI must produce deterministic explanations

AI must never generate credentials or tokens

AI must never bypass authentication

AI must be strictly read-only

AI output must be explainable and auditable

12. Operational Rules & User Preferences
Deep Thinking & Verification

All architectural decisions must be:

Clearly explained

Logically justified

Security-focused

Explicit Approval Required

No major change may be:

Written

Implemented

Refactored

without explicit user permission.

Structure-First Rule

Folder structures explained before creation

Purpose clarified before implementation

Pre-Action Explanation

Before any code or file creation:

Explain what will be done

Explain why it is required

External Code Review (Pro Mode)

Any external suggestions must be evaluated for:

Security

Scalability

Alignment with CryptexDrive goals

Strict Permission Protocol

Actions require confirmation:

Example: “Proceed”

13. Virtual Environment & Execution Rules

Due to environment constraints:

No automatic execution

Commands provided for manual use only

Standard Execution Pattern

Activate virtual environment
Run application manually

Example pattern:

venv\Scripts\activate

python app.py

14. Current State Summary

CryptexDrive is currently a fully functional secure backend system with:

Multi-step authentication

Verified OTP workflow

Dynamic ID authorization

Secure file handling

Clean modular design

The system is stable, review-ready, and expandable.

CryptexDrive – Project Structure Architecture
CryptexDrive/
│
├── cloud/                      # Cloud & storage abstraction
│   └── skystore.py             # Storage helper (future cloud extension)
│
├── docs/                       # Project documentation & notes
│
├── engine/                     # Core security & authentication engine
│   ├── __init__.py
│   ├── auth.py                 # JWT (Dynamic ID) authorization middleware
│   ├── gatekeeper.py           # User auth, OTP logic, password verification
│   ├── phantomid.py            # Dynamic ID (JWT) generator
│   └── vaultcore.py            # Security utilities (reserved for expansion)
│
├── static/                     # Frontend static assets
│   ├── script.js               # Frontend logic
│   └── styles.css              # UI styling
│
├── templates/                  # HTML templates
│   └── index.html              # Main UI page
│
├── uploads/                    # User file storage
│   └── afz/                    # Per-user isolated directory
│
├── venv/                       # Python virtual environment
│
├── app.py                      # Application entry point (Flask server)
├── config.py                   # Configuration (mail, secrets, settings)
├── cryptex.db                  # SQLite database
└── database.py                 # Database helper utilities

🏁 Project Status Summary
Component	Status
Login	✅ Completed
OTP	✅ Completed
Dynamic ID	✅ Completed
File Upload	✅ Completed
Authorization	✅ Completed
Frontend Integration	✅ Basic Impl
Cloud Deployment	❌ Pending
