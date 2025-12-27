import subprocess
import os
import sys

def run_script(script_name):
    print(f"\n>>> Running {script_name}...")
    try:
        # Using sys.executable to ensure we use the same python environment
        result = subprocess.run([sys.executable, script_name], check=True)
        print(f">>> {script_name} completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"!!! Error running {script_name}: {e}")
        return False

def main():
    scripts = [
        "1_organize_photos.py",
        "2_cleanup_modified.py",
        "3_update_metadata.py",
        "4_final_cleanup.py",
        "5_filter_by_date.py"
    ]

    print("==========================================")
    print("   Google Photos Takeout Orchestrator     ")
    print("==========================================")
    print(f"Starting the organization process in: {os.getcwd()}")
    
    for script in scripts:
        if not os.path.exists(script):
            print(f"Warning: {script} not found, skipping.")
            continue
            
        success = run_script(script)
        if not success:
            print(f"\nExecution halted due to error in {script}.")
            sys.exit(1)

    print("\n==========================================")
    print("   ALL STEPS COMPLETED SUCCESSFULLY!      ")
    print("==========================================")
    print("Your photos are organized in 'Unified_photos'.")
    print("Excluded photos are in '_Excluded_by_Date'.")
    print("You can use 6_revert_filter.py to undo the filtering if needed.")

if __name__ == "__main__":
    main()
