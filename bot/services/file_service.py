import os
import time
import logging
from bot.config import TEMP_DIR

def get_temp_path(user_id: int, suffix: str = ".jpg") -> str:
    """Returns a unique temporary file path for a user."""
    os.makedirs(TEMP_DIR, exist_ok=True)
    timestamp = int(time.time() * 1000)
    return os.path.join(TEMP_DIR, f"{user_id}_{timestamp}{suffix}")

async def save_photo(bot, file_id: str, user_id: int) -> str:
    """Downloads photo from Telegram, saves to TEMP_DIR, returns local path"""
    file_info = await bot.get_file(file_id)
    local_path = get_temp_path(user_id, ".jpg")
    await bot.download_file(file_info.file_path, local_path)
    return local_path

def delete_file(path: str) -> None:
    """Silently deletes file, logs warning if file not found"""
    try:
        if os.path.exists(path):
            os.remove(path)
            logging.info(f"Deleted temp file: {path}")
        else:
            logging.warning(f"File not found for deletion: {path}")
    except Exception as e:
        logging.error(f"Error deleting file {path}: {e}")

def cleanup_old_files(max_age_minutes: int = 60) -> int:
    """Deletes temp files older than max_age_minutes, returns count deleted"""
    count = 0
    if not os.path.exists(TEMP_DIR):
        return count
        
    now = time.time()
    for filename in os.listdir(TEMP_DIR):
        filepath = os.path.join(TEMP_DIR, filename)
        if os.path.isfile(filepath):
            file_age = now - os.path.getmtime(filepath)
            if file_age > max_age_minutes * 60:
                delete_file(filepath)
                count += 1
    return count
