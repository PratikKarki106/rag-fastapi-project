# app/utils/file_utils.py
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.config.settings import settings
import os
import shutil

def validate_file(file: UploadFile):
    """Validate uploaded file"""
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    return file_ext

async def save_upload_file(file: UploadFile) -> tuple[str, int]:
    """
    Save uploaded file to disk
    Returns: (file_path, file_size)
    """
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix
    base_name = Path(file.filename).stem
    file_path = upload_dir / f"{base_name}_{os.urandom(4).hex()}{file_ext}"
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = file_path.stat().st_size
        
        # Check file size
        if file_size > settings.MAX_FILE_SIZE:
            file_path.unlink()  # Delete file
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        return str(file_path), file_size
    
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")