import os
import shutil
import glob
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("organization_log.txt", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

DESTINATION_DIR = os.path.abspath("Unified_photos")
ROOT_DIR = os.getcwd()

def get_unique_filename(directory, filename):
    """
    Generates a unique filename if the file already exists in the directory.
    Renames to filename_1, filename_2, etc.
    """
    name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{name}_{counter}{ext}"
        counter += 1
    
    return new_filename

def are_files_identical(file1, file2):
    """
    Checks if two files are identical by comparing size.
    (Could extend to hash check if needed, but size is a good first proxy for speed)
    """
    try:
        s1 = os.path.getsize(file1)
        s2 = os.path.getsize(file2)
        return s1 == s2
    except OSError:
        return False

def organize_photos():
    if not os.path.exists(DESTINATION_DIR):
        os.makedirs(DESTINATION_DIR)
        logging.info(f"Created destination directory: {DESTINATION_DIR}")

    # Find all takeout directories
    takeout_dirs = glob.glob("takeout-*")
    logging.info(f"Found {len(takeout_dirs)} takeout directories: {takeout_dirs}")

    total_moved = 0
    total_skipped = 0
    total_renamed = 0

    for takeout_dir in takeout_dirs:
        # Locate the Google Photos folder inside
        # It could be 'Takeout/Google Photos' or similar. 
        # listing to be sure, catching 'Takeout' first
        takeout_internal = os.path.join(takeout_dir, "Takeout")
        
        if not os.path.exists(takeout_internal):
            logging.warning(f"Could not find 'Takeout' folder in {takeout_dir}, skipping.")
            continue

        google_photos_path = os.path.join(takeout_internal, "Google Photos")
        # Handle potential non-breaking space issues or case sensitivity
        # By finding the folder that looks like 'Google Photos'
        if not os.path.exists(google_photos_path):
             # Try to find it loosely
             children = os.listdir(takeout_internal)
             found = False
             for child in children:
                 if "Google" in child and "Photos" in child:
                     google_photos_path = os.path.join(takeout_internal, child)
                     found = True
                     break
             if not found:
                 logging.warning(f"Could not find 'Google Photos' folder in {takeout_internal}, skipping.")
                 continue

        logging.info(f"Processing source: {google_photos_path}")
        
        # Iterate over albums
        albums = [d for d in os.listdir(google_photos_path) if os.path.isdir(os.path.join(google_photos_path, d))]
        
        for album in albums:
            source_album_path = os.path.join(google_photos_path, album)
            dest_album_path = os.path.join(DESTINATION_DIR, album)

            if not os.path.exists(dest_album_path):
                os.makedirs(dest_album_path)
            
            # Use os.scandir for better performance with many files
            with os.scandir(source_album_path) as it:
                for entry in it:
                    if entry.is_file():
                        source_file = entry.path
                        filename = entry.name
                        dest_file = os.path.join(dest_album_path, filename)

                        if os.path.exists(dest_file):
                            # File exists, check if identical
                            if are_files_identical(source_file, dest_file):
                                logging.info(f"Duplicate found (identical size): {filename} in {album}. Skipping.")
                                total_skipped += 1
                            else:
                                # Not identical, rename
                                new_filename = get_unique_filename(dest_album_path, filename)
                                dest_file_renamed = os.path.join(dest_album_path, new_filename)
                                shutil.move(source_file, dest_file_renamed)
                                logging.info(f"Conflict (diff size): Moved {filename} to {new_filename} in {album}.")
                                total_renamed += 1
                                total_moved += 1
                        else:
                            # Move file
                            shutil.move(source_file, dest_file)
                            total_moved += 1

    logging.info("="*30)
    logging.info("PROCESSING COMPLETE")
    logging.info(f"Total files moved: {total_moved}")
    logging.info(f"Total files renamed (conflicts kept): {total_renamed}")
    logging.info(f"Total duplicates skipped: {total_skipped}")

if __name__ == "__main__":
    organize_photos()
