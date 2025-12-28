import os
import logging
import hashlib
from collections import defaultdict

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

def calculate_hash(file_path):
    """Calculate SHA256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        logging.error(f"Error calculating hash for {file_path}: {e}")
        return None

def remove_duplicates(target_dir):
    """Find and remove duplicate files based on content hash, with folder priority."""
    hashes = defaultdict(list)
    count_duplicates = 0

    logging.info("Scanning for duplicates (calculating hashes)...")
    for root, _, files in os.walk(target_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            # Skip json files as they are handled separately or deleted
            if filename.lower().endswith(".json"):
                continue
            
            file_hash = calculate_hash(file_path)
            if file_hash:
                hashes[file_hash].append(file_path)

    logging.info("Processing duplicates...")
    for file_hash, paths in hashes.items():
        if len(paths) > 1:
            # Sort paths: prioritizing those IN "Photos de " folders
            # We want to KEEP one file. 
            # Logic: 
            # 1. Paths starting with "Photos de " are higher priority.
            # 2. Within same priority, shorter paths might be preferred (sturdier)
            
            def get_priority(path):
                # Get the immediate parent folder name
                parent_folder = os.path.basename(os.path.dirname(path))
                if parent_folder.startswith("Photos de "):
                    return 0 # Higher priority
                return 1 # Lower priority

            # Sort by priority (0 first), then by path length
            paths.sort(key=lambda p: (get_priority(p), len(p)))
            
            # The first one is the one we KEEP
            to_keep = paths[0]
            to_delete = paths[1:]
            
            for path in to_delete:
                try:
                    os.remove(path)
                    count_duplicates += 1
                    logging.info(f"Deleted duplicate: {path} (Keeping: {to_keep})")
                except OSError as e:
                    logging.error(f"Error deleting duplicate {path}: {e}")
    
    return count_duplicates

def final_cleanup():
    if not os.path.exists(TARGET_DIR):
        logging.error(f"Target directory {TARGET_DIR} does not exist.")
        return

    count_json = 0
    count_mp = 0
    count_folders = 0
    count_duplicates = 0

    # 0. Remove duplicates first (based on hash)
    count_duplicates = remove_duplicates(TARGET_DIR)

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
    logging.info(f"Duplicate files deleted: {count_duplicates}")
    logging.info(f"Empty folders deleted: {count_folders}")

if __name__ == "__main__":
    final_cleanup()
