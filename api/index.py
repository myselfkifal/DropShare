from flask import Flask, send_from_directory, abort, jsonify
from flask_cors import CORS
import os
import threading
import time
from .database import engine, Base, SessionLocal
from .routes.upload import upload_bp
from .routes.download import download_bp
from .routes.cleanup import cleanup_expired_files

# Create tables
Base.metadata.create_all(bind=engine)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

if os.environ.get('VERCEL'):
    UPLOAD_DIR = "/tmp/uploads"
else:
    UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024 # 500 MB

# Register Blueprints first so their routes have priority
app.register_blueprint(upload_bp)
app.register_blueprint(download_bp)

# Specific route for the homepage
@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

# Specific route for assets (CSS, JS, etc.)
@app.route('/<filename>')
def serve_static_root(filename):
    if filename.endswith(('.css', '.js', '.png', '.jpg', '.ico', '.svg')):
        return send_from_directory(FRONTEND_DIR, filename)
    return abort(404)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Rate limit exceeded", detail=str(e.description)), 429

def run_cleanup_thread():
    while True:
        try:
            db = SessionLocal()
            try:
                cleanup_expired_files(db, UPLOAD_DIR)
            finally:
                db.close()
        except Exception as e:
            print(f"Cleanup thread error: {e}")
        time.sleep(3600)

if __name__ == "__main__":
    cleanup_thread = threading.Thread(target=run_cleanup_thread, daemon=True)
    cleanup_thread.start()
    app.run(port=8000, host='0.0.0.0')
