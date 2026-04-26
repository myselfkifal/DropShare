from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import os
import re
import zipfile
import time
import io
from werkzeug.security import generate_password_hash
from database import SessionLocal
from models import FileModel
from utils.security import is_allowed_file, generate_secure_filename, generate_file_code

upload_bp = Blueprint('upload', __name__)

MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if os.environ.get('VERCEL'):
    UPLOAD_DIR = "/tmp/uploads"
else:
    UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def format_file_size(size_bytes):
    if size_bytes == 0: return "0B"
    size_name = ("B", "KB", "MB", "GB")
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

def get_local_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    files = request.files.getlist('files[]')
    if not files or all(f.filename == '' for f in files):
        return jsonify({"detail": "No file part"}), 400
    
    expiry = request.form.get('expiry')
    custom_alias = request.form.get('custom_alias', '').strip()
    is_one_time = request.form.get('is_one_time') == 'true'
    password = request.form.get('password', '').strip()

    db = SessionLocal()
    try:
        if custom_alias:
            if not re.match(r'^[a-zA-Z0-9_-]+$', custom_alias):
                return jsonify({"detail": "Custom link error"}), 400
            exists = db.query(FileModel).filter(FileModel.file_code == custom_alias).first()
            if exists: return jsonify({"detail": "Link taken"}), 400
            file_code = custom_alias
        else:
            file_code = generate_file_code()

        password_hash = generate_password_hash(password) if password else None
        now = datetime.utcnow()
        expires_at = now + (timedelta(hours=1) if expiry == "1h" else timedelta(days=1) if expiry == "24h" else timedelta(days=7))

        if len(files) > 1:
            zip_filename = f"DropShare_Package_{int(time.time())}.zip"
            stored_filename = f"{file_code}_{zip_filename}"
            final_path = os.path.join(UPLOAD_DIR, stored_filename)
            
            with zipfile.ZipFile(final_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for f in files:
                    if f and is_allowed_file(f.filename):
                        temp_path = os.path.join(UPLOAD_DIR, f"temp_{f.filename}")
                        f.save(temp_path)
                        zipf.write(temp_path, f.filename)
                        os.remove(temp_path)
            
            original_filename = "Collection_Of_Files.zip"
        else:
            file = files[0]
            if not is_allowed_file(file.filename):
                return jsonify({"detail": "File type not allowed"}), 400
            stored_filename = f"{file_code}_{generate_secure_filename(file.filename)}"
            final_path = os.path.join(UPLOAD_DIR, stored_filename)
            file.save(final_path)
            original_filename = file.filename

        file_size_readable = format_file_size(os.path.getsize(final_path))

        db_file = FileModel(
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_code=file_code,
            file_size=file_size_readable,
            is_one_time=1 if is_one_time else 0,
            password_hash=password_hash,
            download_count=0,
            created_at=now,
            expires_at=expires_at
        )
        db.add(db_file)
        db.commit()

        base_url = request.host_url.rstrip("/")
        file_url = f"{base_url}/file/{file_code}"
        network_url = f"http://{get_local_ip()}:8000/file/{file_code}"

        return jsonify({
            "file_url": file_url,
            "network_file_url": network_url,
            "expires_at": expires_at.isoformat()
        })
    finally:
        db.close()
