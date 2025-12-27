import os
import json
import glob
import logging
import time
from ctypes import windll, Structure, byref, c_longlong, c_int, create_unicode_buffer
from ctypes.wintypes import HANDLE, DWORD, LPVOID

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("metadata_update_log.txt", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

TARGET_DIR = os.path.abspath("Unified_photos")

# Windows API Structures
class FILETIME(Structure):
    _fields_ = [("dwLowDateTime", DWORD),
                ("dwHighDateTime", DWORD)]

def set_file_creation_time(path, timestamp):
    """
    Sets the creation time of a file on Windows.
    Timestamp is a unix timestamp (seconds since epoch).
    """
    try:
        # Convert unix timestamp to Windows FileTime (100-nanosecond intervals since Jan 1, 1601)
        # Unix epoch (Jan 1 1970) is 116444736000000000 intervals after Windows epoch
        windows_ticks = int((timestamp * 10000000) + 116444736000000000)
        
        ft = FILETIME()
        ft.dwLowDateTime = windows_ticks & 0xFFFFFFFF
        ft.dwHighDateTime = windows_ticks >> 32
        
        # Open file
        handle = windll.kernel32.CreateFileW(
            path, 
            256, # GENERIC_WRITE (0x40000000) -> using 256 for FILE_WRITE_ATTRIBUTES equivalent logic
            0, 
            None, 
            3, # OPEN_EXISTING 
            128, # FILE_ATTRIBUTE_NORMAL
            None
        )
        
        if handle == -1:
            logging.warning(f"Failed to open file handle for {path}")
            return False

        # SetFileTime(handle, creation_time, access_time, write_time)
        # We only strictly care about creation time here as os.utime handles the rest, 
        # but os.utime might be more stable for access/write.
        # Let's try to set all three to be consistent if strict sync is seemingly desired?
        # User said: "date de création du fichier ... et la date de prise de vue"
        # Since we use os.utime later for mod/access, we can just pass ft for all or just creation.
        # Passing None (0 pointer) leaves it unchanged.
        
        result = windll.kernel32.SetFileTime(handle, byref(ft), None, None)
        windll.kernel32.CloseHandle(handle)
        
        if result == 0:
            logging.warning(f"SetFileTime failed for {path}")
            return False
            
        return True
        
    except Exception as e:
        logging.error(f"Error setting creation time for {path}: {e}")
        return False

def find_json_file(file_path):
    """
    Attempts to find the associated JSON file for a given file path.
    Handles standard naming and truncated extensions.
    """
    candidates = [
        file_path + ".json",
        file_path + ".supplemental-metadata.json"
    ]
    
    for cand in candidates:
        if os.path.exists(cand):
            return cand
            
    directory = os.path.dirname(file_path)
    pattern = glob.escape(file_path) + ".*.json"
    matches = glob.glob(pattern)
    
    if matches:
        return matches[0]
        
    return None

def update_file_timestamp(file_path, json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        ts_creation = None      # JSON creationTime -> Windows Creation Date
        ts_modification = None  # JSON modificationTime -> Windows Modification Date
        ts_taken = None         # JSON photoTakenTime -> Windows Access Date (compromise)
        
        # 1. Parse creationTime
        if "creationTime" in data and "timestamp" in data["creationTime"]:
            ts_creation = float(data["creationTime"]["timestamp"])
        
        # 2. Parse modificationTime
        if "modificationTime" in data and "timestamp" in data["modificationTime"]:
             ts_modification = float(data["modificationTime"]["timestamp"])
        
        # 3. Parse photoTakenTime
        if "photoTakenTime" in data and "timestamp" in data["photoTakenTime"]:
             ts_taken = float(data["photoTakenTime"]["timestamp"])

        # Fallbacks to ensure we don't leave fields at current (extraction) time if any info exists
        # If user specific mapping is missing, we propagate available info
        if not ts_creation:
            ts_creation = ts_taken
        if not ts_modification:
            ts_modification = ts_creation
        if not ts_taken:
            ts_taken = ts_creation

        if ts_creation or ts_modification or ts_taken:
            # Update via Windows API
            # Convert unix timestamps to Windows FileTime
            # (Logic remains same, but we set all three)
            
            def to_ft(ts):
                if not ts: return None
                ticks = int((ts * 10000000) + 116444736000000000)
                ft = FILETIME()
                ft.dwLowDateTime = ticks & 0xFFFFFFFF
                ft.dwHighDateTime = ticks >> 32
                return ft

            ft_creation = to_ft(ts_creation)
            ft_modification = to_ft(ts_modification)
            ft_taken = to_ft(ts_taken)

            # Open file
            handle = windll.kernel32.CreateFileW(file_path, 256, 0, None, 3, 128, None)
            if handle != -1:
                # SetFileTime(handle, lpCreationTime, lpLastAccessTime, lpLastWriteTime)
                # Note: Windows Explorer often shows 'Date' based on EXIF, 
                # but if we follow user's mapping:
                # Creation -> creationTime
                # Modification -> modificationTime
                # Access -> photoTakenTime (using this as it's the 3rd available slot)
                windll.kernel32.SetFileTime(
                    handle, 
                    byref(ft_creation) if ft_creation else None,
                    byref(ft_taken) if ft_taken else None,
                    byref(ft_modification) if ft_modification else None
                )
                windll.kernel32.CloseHandle(handle)
                
                logging.info(f"Updated {os.path.basename(file_path)}: Creation={ts_creation}, Mod={ts_modification}, Taken(Access)={ts_taken}")
                return True
            else:
                logging.warning(f"Failed to open file handle for {file_path}")
                return False
        else:
            logging.warning(f"No valid timestamps found in {os.path.basename(json_path)}")
            return False
            
    except Exception as e:
        logging.error(f"Error processing {file_path} with {json_path}: {e}")
        return False

def main():
    if not os.path.exists(TARGET_DIR):
        logging.error(f"Target directory {TARGET_DIR} does not exist.")
        return

    count_processed = 0
    count_updated = 0
    count_missing_json = 0

    # Walk through the directory
    for root, dirs, files in os.walk(TARGET_DIR):
        for filename in files:
            # Skip json files themselves
            if filename.lower().endswith(".json"):
                continue
                
            file_path = os.path.join(root, filename)
            
            # Find associated JSON
            json_path = find_json_file(file_path)
            
            if json_path:
                if update_file_timestamp(file_path, json_path):
                    count_updated += 1
            else:
                count_missing_json += 1
                
            count_processed += 1
            
            if count_processed % 100 == 0:
                print(f"Processed {count_processed} files...", end='\r')

    logging.info("="*30)
    logging.info(f"Total processed: {count_processed}")
    logging.info(f"Total updated: {count_updated}")
    logging.info(f"Files without JSON: {count_missing_json}")

if __name__ == "__main__":
    main()
