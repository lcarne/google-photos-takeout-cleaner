import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cleanup_log.txt", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

TARGET_DIR = os.path.abspath("Unified_photos")

def cleanup_modified_files():
    if not os.path.exists(TARGET_DIR):
        logging.error(f"Target directory {TARGET_DIR} does not exist.")
        return

    count_replaced = 0
    count_renamed = 0
    count_errors = 0

    for root, dirs, files in os.walk(TARGET_DIR):
        for filename in files:
            # Check for pattern *-modifié.*
            # Be careful not to match files that just happen to have modified in the name but not as a suffix before extension
            # But the user said "suffixés en -modifié", so we look for that exact ending before extension.
            
            name, ext = os.path.splitext(filename)
            if name.endswith("-modifié"):
                original_name_base = name[:-len("-modifié")]
                original_filename = original_name_base + ext
                
                modified_file_path = os.path.join(root, filename)
                original_file_path = os.path.join(root, original_filename)
                
                try:
                    if os.path.exists(original_file_path):
                        # Delete original, rename modified to original
                        os.remove(original_file_path)
                        os.rename(modified_file_path, original_file_path)
                        logging.info(f"Replaced: {original_filename} with {filename}")
                        count_replaced += 1
                    else:
                        # Just rename modified to original
                        os.rename(modified_file_path, original_file_path)
                        logging.info(f"Renamed: {filename} to {original_filename} (original missing)")
                        count_renamed += 1
                except OSError as e:
                    logging.error(f"Error processing {filename}: {e}")
                    count_errors += 1

    logging.info("="*30)
    logging.info(f"Total replaced: {count_replaced}")
    logging.info(f"Total renamed (no original): {count_renamed}")
    logging.info(f"Errors: {count_errors}")

if __name__ == "__main__":
    cleanup_modified_files()
