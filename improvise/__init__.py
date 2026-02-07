from .db import init_enhanced_tables
from .vault import Vault
from .ai_analyzer import AIAnalyzer
from .audit import AuditLogger
from .security import SecurityHarden

def bootstrap_improvements():
    """Initializes all improvised features."""
    init_enhanced_tables()
    print("[SYSTEM] CryptexDrive Improvised Modules Loaded.")
