import os
import shutil
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("filter_by_date_log.txt", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

TARGET_DIR = os.path.abspath("Unified_photos")
EXCLUDED_DIR = os.path.abspath("_Excluded_by_Date")

# Range: 18/08/2013 to 25/12/2020
START_DATE = datetime(2013, 8, 18)
END_DATE = datetime(2020, 12, 25, 23, 59, 59)

def filter_photos():
    if not os.path.exists(TARGET_DIR):
        logging.error(f"Target directory {TARGET_DIR} does not exist.")
        return

    if not os.path.exists(EXCLUDED_DIR):
        os.makedirs(EXCLUDED_DIR)

    count_kept = 0
    count_excluded = 0
    count_folders_cleaned = 0

    # 1. Check all files
    for root, dirs, files in os.walk(TARGET_DIR):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                stats = os.stat(file_path)
                
                # Best photo date is Last Access Time (where we mapped photoTakenTime)
                # OR Creation Time (creationTime) 
                # We'll check the EARLIEST of the three standard dates just in case
                # but primarily focus on the Access time (taken) and Creation time (cloud)
                atime = datetime.fromtimestamp(stats.st_atime)
                ctime = datetime.fromtimestamp(stats.st_ctime)
                mtime = datetime.fromtimestamp(stats.st_mtime)
                
                # In our setup: atime=Taken, ctime=CloudCreation, mtime=Modification
                # We keep if ANY of these important dates are in range
                is_in_range = (START_DATE <= atime <= END_DATE) or \
                              (START_DATE <= ctime <= END_DATE) or \
                              (START_DATE <= mtime <= END_DATE)

                if is_in_range:
                    count_kept += 1
                else:
                    # Move to excluded while preserving relative path
                    rel_path = os.path.relpath(file_path, TARGET_DIR)
                    target_excluded_path = os.path.join(EXCLUDED_DIR, rel_path)
                    
                    # Create subfolder in excluded if needed
                    os.makedirs(os.path.dirname(target_excluded_path), exist_ok=True)
                    
                    shutil.move(file_path, target_excluded_path)
                    count_excluded += 1
                    logging.info(f"Excluded {filename} (Dates: A={atime.date()}, C={ctime.date()}, M={mtime.date()} are outside range)")
                    
            except Exception as e:
                logging.error(f"Error processing {file_path}: {e}")

    # 2. Cleanup empty folders in source
    for root, dirs, files in os.walk(TARGET_DIR, topdown=False):
        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    count_folders_cleaned += 1
            except OSError:
                pass

    logging.info("="*30)
    logging.info(f"Photos kept in target: {count_kept}")
    logging.info(f"Photos moved to exclusion: {count_excluded}")
    logging.info(f"Empty source folders removed: {count_folders_cleaned}")

if __name__ == "__main__":
    filter_photos()
