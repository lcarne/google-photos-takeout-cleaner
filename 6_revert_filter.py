import os
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("revert_filter_log.txt", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

TARGET_DIR = os.path.abspath("Unified_photos")
EXCLUDED_DIR = os.path.abspath("_Excluded_by_Date")

def revert_filter():
    if not os.path.exists(EXCLUDED_DIR):
        logging.info("No excluded photos directory found. Nothing to revert.")
        return

    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)

    count_reverted = 0
    count_folders_cleaned = 0

    # 1. Move everything back from excluded folder
    for root, dirs, files in os.walk(EXCLUDED_DIR):
        for filename in files:
            file_excluded_path = os.path.join(root, filename)
            
            # Reconstruct original path in target
            rel_path = os.path.relpath(file_excluded_path, EXCLUDED_DIR)
            target_original_path = os.path.join(TARGET_DIR, rel_path)
            
            try:
                # Ensure destination subfolder exists
                os.makedirs(os.path.dirname(target_original_path), exist_ok=True)
                
                # Move back (shutil.move handles overwriting or errors if exists)
                shutil.move(file_excluded_path, target_original_path)
                count_reverted += 1
                # logging.info(f"Reverted: {rel_path}")
            except Exception as e:
                logging.error(f"Error reverting {file_excluded_path}: {e}")

    # 2. Cleanup empty folders in excluded directory
    for root, dirs, files in os.walk(EXCLUDED_DIR, topdown=False):
        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    count_folders_cleaned += 1
            except OSError:
                pass
    
    # Cleanup root excluded folder if empty
    try:
        if os.path.exists(EXCLUDED_DIR) and not os.listdir(EXCLUDED_DIR):
            os.rmdir(EXCLUDED_DIR)
    except OSError:
        pass

    logging.info("="*30)
    logging.info(f"Photos reverted to target: {count_reverted}")
    logging.info(f"Empty exclusion folders removed: {count_folders_cleaned}")

if __name__ == "__main__":
    revert_filter()
