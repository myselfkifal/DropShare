from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base

class FileModel(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String)
    stored_filename = Column(String)
    file_code = Column(String, unique=True, index=True)
    file_size = Column(String)  # Human readable size
    is_one_time = Column(Integer, default=0)  # 0: No, 1: Yes
    download_count = Column(Integer, default=0)
    password_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
