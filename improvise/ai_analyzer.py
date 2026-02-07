import os
# import magic # Requires python-magic
from .db import get_db_context

class AIAnalyzer:
    """The Cryptex AI Engine: Analyzes files for risks and metadata anomalies."""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.txt', '.docx'}
    
    @staticmethod
    def analyze_file(file_path, filename, username):
        file_size = os.path.getsize(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        risk_score = 0
        reasons = []

        # 1. Extension check
        if ext not in AIAnalyzer.ALLOWED_EXTENSIONS:
            risk_score += 50
            reasons.append(f"Uncommon file extension: {ext}")

        # 2. Size anomalies
        if file_size > 5 * 1024 * 1024: # > 5MB
            risk_score += 20
            reasons.append("Large file size for standard document")

        # 3. Mime-type mismatch (Simulated AI Check)
        # In a real scenario, we'd use 'magic' to check if content matches extension
        # risk_score += 30 (if mismatch)

        analysis_summary = "; ".join(reasons) if reasons else "File appears safe."
        
        # Save analysis to DB
        with get_db_context() as db:
            db.execute("""
                INSERT INTO file_metadata (filename, owner, size, risk_score, ai_analysis)
                VALUES (?, ?, ?, ?, ?)
            """, (filename, username, file_size, risk_score, analysis_summary))
            
        return {
            "risk_score": risk_score,
            "analysis": analysis_summary,
            "safe": risk_score < 70
        }
