from flask import Blueprint, send_from_directory, abort, jsonify, request
import os
from datetime import datetime
from werkzeug.security import check_password_hash
from ..database import SessionLocal
from ..models import FileModel

download_bp = Blueprint('download', __name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

if os.environ.get('VERCEL'):
    UPLOAD_DIR = "/tmp/uploads"
else:
    UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")

@download_bp.route("/file/<code>", methods=["GET"])
def landing_page(code):
    return send_from_directory(FRONTEND_DIR, 'landing.html')

@download_bp.route("/api/file/<code>", methods=["GET"])
def get_file_metadata(code):
    db = SessionLocal()
    try:
        db_file = db.query(FileModel).filter(FileModel.file_code == code).first()
        if not db_file: return jsonify({"detail": "File not found"}), 404
        if db_file.expires_at < datetime.utcnow(): return jsonify({"detail": "Link expired"}), 410
        if db_file.is_one_time and db_file.download_count > 0:
            return jsonify({"detail": "This one-time link has already been used"}), 410

        return jsonify({
            "filename": db_file.original_filename if not db_file.password_hash else "Protected File",
            "size": db_file.file_size if not db_file.password_hash else "? KB",
            "created_at": db_file.created_at.isoformat(),
            "expires_at": db_file.expires_at.isoformat(),
            "is_one_time": bool(db_file.is_one_time),
            "is_image": not db_file.password_hash and db_file.original_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')),
            "password_protected": bool(db_file.password_hash)
        })
    finally:
        db.close()

@download_bp.route("/api/file/<code>/unlock", methods=["POST"])
def unlock_file(code):
    db = SessionLocal()
    try:
        db_file = db.query(FileModel).filter(FileModel.file_code == code).first()
        if not db_file: return jsonify({"detail": "File not found"}), 404
        
        password = request.json.get('password', '')
        if not db_file.password_hash or check_password_hash(db_file.password_hash, password):
            return jsonify({
                "filename": db_file.original_filename,
                "size": db_file.file_size,
                "is_image": db_file.original_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')),
                "unlocked": True
            })
        return jsonify({"detail": "Incorrect password"}), 401
    finally:
        db.close()

@download_bp.route("/download/<code>", methods=["GET"])
def execute_download(code):
    password = request.args.get('p', '')
    db = SessionLocal()
    try:
        db_file = db.query(FileModel).filter(FileModel.file_code == code).first()
        if not db_file: abort(404)
        if db_file.expires_at < datetime.utcnow(): return jsonify({"detail": "Link expired"}), 410
        if db_file.is_one_time and db_file.download_count > 0: return jsonify({"detail": "Already downloaded"}), 410

        # Check password if set
        if db_file.password_hash and not check_password_hash(db_file.password_hash, password):
            abort(401, description="Password required")

        file_path = os.path.join(UPLOAD_DIR, db_file.stored_filename)
        if not os.path.exists(file_path): abort(404)

        db_file.download_count += 1
        db.commit()

        return send_from_directory(
            UPLOAD_DIR, 
            db_file.stored_filename, 
            as_attachment=True, 
            download_name=db_file.original_filename
        )
    finally:
        db.close()
