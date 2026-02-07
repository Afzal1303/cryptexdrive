import os
from cryptography.fernet import Fernet
from config import SECRET_KEY
import base64
import hashlib

# Derive a consistent 32-byte key from the project's SECRET_KEY
def get_vault_key():
    key = hashlib.sha256(SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(key)

class Vault:
    """Handles file encryption and decryption at rest."""
    
    @staticmethod
    def encrypt_file(file_path):
        fernet = Fernet(get_vault_key())
        with open(file_path, "rb") as f:
            data = f.read()
        
        encrypted_data = fernet.encrypt(data)
        with open(file_path, "wb") as f:
            f.write(encrypted_data)
        return True

    @staticmethod
    def decrypt_file_data(file_path):
        fernet = Fernet(get_vault_key())
        with open(file_path, "rb") as f:
            encrypted_data = f.read()
        
        return fernet.decrypt(encrypted_data)
