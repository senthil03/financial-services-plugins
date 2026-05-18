import os
import shutil
import tempfile
from datetime import datetime

def run_backup():
    # 1. Define paths to backup
    reports_path = r"d:\Projects\Antigravity\Financial AI\Reports"
    user_profile = os.environ.get("USERPROFILE", "")
    ai_brain_path = os.path.join(user_profile, ".gemini", "antigravity")

    # 2. Determine backup destination (OneDrive -> Fallback to Documents)
    onedrive_corporate = os.path.join(user_profile, "OneDrive - Personal")
    onedrive_personal = os.path.join(user_profile, "OneDrive")
    documents_dir = os.path.join(user_profile, "Documents")

    if os.path.exists(onedrive_corporate):
        backup_dest_dir = os.path.join(onedrive_corporate, "Antigravity_Backups")
    elif os.path.exists(onedrive_personal):
        backup_dest_dir = os.path.join(onedrive_personal, "Antigravity_Backups")
    else:
        backup_dest_dir = os.path.join(documents_dir, "Antigravity_Backups")

    os.makedirs(backup_dest_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    temp_dir = os.path.join(tempfile.gettempdir(), f"Antigravity_Backup_Temp_{timestamp}")
    os.makedirs(temp_dir, exist_ok=True)

    print("---")
    print("[INFO] Initializing Antigravity Workspace Backup...")
    print("---")

    # Copy Reports
    if os.path.exists(reports_path):
        print("[INFO] Copying daily strategy Reports...")
        shutil.copytree(reports_path, os.path.join(temp_dir, "Reports"), dirs_exist_ok=True)
    else:
        print(f"[WARN] Warning: Reports directory not found at {reports_path}")

    # Copy AI Brain
    if os.path.exists(ai_brain_path):
        print("[INFO] Copying AI Brain Persistent Memory (Conversation Logs)...")
        # Ignore locks/temp files
        def ignore_patterns(path, names):
            return [n for n in names if n.endswith(".lock") or n.endswith(".sock")]
        shutil.copytree(ai_brain_path, os.path.join(temp_dir, "AI_Brain"), dirs_exist_ok=True, ignore=ignore_patterns)
    else:
        print(f"[WARN] Warning: AI Brain not found at {ai_brain_path}")

    # Create ZIP
    zip_base_name = os.path.join(backup_dest_dir, f"Antigravity_Backup_{timestamp}")
    print("[INFO] Compressing directories into secure ZIP archive...")
    shutil.make_archive(zip_base_name, 'zip', temp_dir)

    # Enforce Retention Policy (Max 2 Backup Files)
    print("[INFO] Enforcing backup retention policy (Max 2 files)...")
    try:
        backups = [os.path.join(backup_dest_dir, f) for f in os.listdir(backup_dest_dir)
                   if f.startswith("Antigravity_Backup_") and f.endswith(".zip")]
        backups.sort()  # Alphabetical sort matches chronological order due to YYYY-MM-DD_HHMMSS
        while len(backups) > 2:
            oldest_backup = backups.pop(0)
            print(f"[CLEANUP] Removing oldest backup: {os.path.basename(oldest_backup)}")
            os.remove(oldest_backup)
    except Exception as e:
        print(f"[WARN] Failed to clean up older backups: {e}")

    # Cleanup temp
    print("[INFO] Cleaning up temporary workspace...")
    shutil.rmtree(temp_dir, ignore_errors=True)

    print("---")
    print("[SUCCESS] Your workspace backup has been securely created!")
    print(f"[SUCCESS] Location: {zip_base_name}.zip")
    print("---")

if __name__ == "__main__":
    run_backup()
