import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("final_cleanup_log.txt", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

TARGET_DIR = os.path.abspath("Unified_photos")

def final_cleanup():
    if not os.path.exists(TARGET_DIR):
        logging.error(f"Target directory {TARGET_DIR} does not exist.")
        return

    count_json = 0
    count_mp = 0
    count_folders = 0

    # 1. Remove .json and .MP files
    for root, dirs, files in os.walk(TARGET_DIR):
        for filename in files:
            file_path = os.path.join(root, filename)
            ext = filename.lower()
            
            if ext.endswith(".json"):
                try:
                    os.remove(file_path)
                    count_json += 1
                except OSError as e:
                    logging.error(f"Error deleting {file_path}: {e}")
            
            elif ext.endswith(".mp"):
                try:
                    os.remove(file_path)
                    count_mp += 1
                except OSError as e:
                    logging.error(f"Error deleting {file_path}: {e}")

    # 2. Remove empty folders (recursively)
    # We walk bottom-up to ensure we catch folders that became empty because their subfolders were deleted
    for root, dirs, files in os.walk(TARGET_DIR, topdown=False):
        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    count_folders += 1
                    # logging.info(f"Removed empty folder: {dir_path}")
            except OSError as e:
                logging.error(f"Error deleting folder {dir_path}: {e}")

    logging.info("="*30)
    logging.info(f"JSON files deleted: {count_json}")
    logging.info(f".MP files deleted: {count_mp}")
    logging.info(f"Empty folders deleted: {count_folders}")

if __name__ == "__main__":
    final_cleanup()
