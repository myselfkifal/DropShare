import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

def get_encryption_key(password, salt=None):
    """
    Generate a 32-byte key from a password and salt.
    """
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_data(data, password):
    """
    Encrypt bytes using Fernet (AES-128 in CBC mode with HMAC).
    Returns (encrypted_data, salt)
    """
    key, salt = get_encryption_key(password)
    f = Fernet(key)
    encrypted = f.encrypt(data)
    return encrypted, salt

def decrypt_data(encrypted_data, password, salt):
    """
    Decrypt bytes using Fernet.
    """
    key, _ = get_encryption_key(password, salt)
    f = Fernet(key)
    return f.decrypt(encrypted_data)
