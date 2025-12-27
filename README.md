# Google Photos Takeout Cleaner

A set of Python scripts to clean, merge, and organize photos from multiple Google Photos Takeout archives.

## Features

- **Merge Albums**: Consolidates photo albums split across multiple `takeout-*.zip` files into a single `Unified_photos` directory.
- **Smart Duplicate Handling**: Skips identical files (by size) and renames conflicting files with different sizes.
- **Metadata Restoration**: Restores file system timestamps (Creation, Modification, and Access dates) using Google's `.json` sidecar files.
- **Cleanup Modified Files**: Replaces original photos with their `-modifié` versions (edited in Google Photos).
- **Cleanup Garbage**: Removes `.json` metadata files and `.MP` (Motion Photo) sidecars once processing is complete.
- **Date Filtering**: Moves photos outside a specific date range (e.g., 2013-2020) to an `_Excluded_by_Date` folder while preserving the folder structure.
- **Revert Filter**: A safety script to move excluded photos back to the main collection.

## How to use

Follow these steps to organize your photos:

1.  **Extract your archives**: Make sure all your Google Takeout ZIP files are extracted. You should have folders like `takeout-20250101T...`.
2.  **Setup the directory**: Place all the `takeout-*` folders in the same directory as these Python scripts.
3.  **Open a terminal**: 
    - On Windows, we recommend using PowerShell or CMD.
    - Navigate to the directory containing the scripts (e.g., `cd C:\Users\YourName\Downloads\extract_gp`).
4.  **Run the orchestrator**:
    Execute the following command:
    ```bash
    python main.py
    ```
5.  **Follow the progress**: The script will guide you through all 5 stages of organization. Once finished, you will find your organized collection in the `Unified_photos` folder.

## Individual Scripts

- `6_revert_filter.py`: Run this manually if you want to undo the date filtering and merge everything back into `Unified_photos`.

## Requirements

- Windows OS (for `ctypes` file time manipulation).
- Python 3.x.

## Limitation

Note: Internal EXIF "Date Taken" tags are not modified as this script relies only on standard libraries to avoid external dependencies. It focuses on OS-level file timestamps which are used by most file explorers for sorting.
