from .db import init_enhanced_tables
from .vault import Vault
from .ai_analyzer import AIAnalyzer
from .audit import AuditLogger
from .security import SecurityHarden
from .self_healing import start_self_healing

def bootstrap_improvements():
    """Initializes all improvised features."""
    init_enhanced_tables()
    start_self_healing()
    print("[SYSTEM] CryptexDrive Improvised Modules Loaded.")
