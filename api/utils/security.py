import os
import uuid
import secrets
import string
from typing import List

# Allowed extensions (expanded for better usability)
ALLOWED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.docx', '.doc', 
    '.txt', '.zip', '.rar', '.7z', '.pdsprj', '.xlsx', '.pptx'
}

def get_file_extension(filename: str) -> str:
    _, ext = os.path.splitext(filename)
    return ext.lower()

def is_allowed_file(filename: str) -> bool:
    ext = get_file_extension(filename)
    return ext in ALLOWED_EXTENSIONS

def generate_secure_filename(original_filename: str) -> str:
    ext = get_file_extension(original_filename)
    random_str = str(uuid.uuid4())
    return f"{random_str}{ext}"

def generate_file_code(length: int = 8) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def sanitize_filename(filename: str) -> str:
    # Basic sanitization to prevent path traversal
    return os.path.basename(filename)
