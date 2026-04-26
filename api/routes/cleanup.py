from sqlalchemy.orm import Session
from datetime import datetime
import os
from ..models import FileModel

def cleanup_expired_files(db: Session, upload_dir: str):
    """
    Finds and deletes expired files from record and disk.
    """
    now = datetime.utcnow()
    expired_files = db.query(FileModel).filter(FileModel.expires_at < now).all()
    
    count = 0
    for file_record in expired_files:
        # Delete from disk
        file_path = os.path.join(upload_dir, file_record.stored_filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
        
        # Delete from DB
        db.delete(file_record)
        count += 1
    
    if count > 0:
        db.commit()
        print(f"Cleaned up {count} expired files.")
    
    return count
