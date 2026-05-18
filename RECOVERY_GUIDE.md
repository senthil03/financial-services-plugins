# 🛡️ Antigravity Workspace Recovery & Restoration Guide

This document outlines the step-by-step instructions for restoring your daily financial strategy Reports, transaction caches, and AI persistent memory in the event of a computer crash or when setting up your environment on a new machine.

---

## 📂 Backup Architecture Overview

Your backup engine is powered by [backup_workspace.py](file:///d:/Projects/Antigravity/Financial%20AI/backup_workspace.py) and automated via Windows Task Scheduler (**`Antigravity_Workspace_Backup`**) to trigger **weekly on Fridays at 6:00 PM (EST)**. 

### **What is Backed Up?**
Every backup is a secure, compressed ZIP archive containing:
1.  **📁 Workspace Strategy Reports**: All daily newsletters, checklists, execution blueprints, and folder README indexes from the `Reports/` directory.
2.  **🧠 AI Brain Persistent Memory**: All local conversation logs, historical strategic context, and localized knowledge items from `C:\Users\vellaichamy\.gemini\antigravity\`.

### **Backup Destination**
Backups are saved directly into your local cloud-synced folder:
📍 **`C:\Users\vellaichamy\OneDrive\Antigravity_Backups\`** (or your active corporate OneDrive folder).
*   *Retention Policy*: **Only the 2 most recent backups are kept** to optimize cloud storage capacity. Older backups are automatically pruned when a new one is successfully created.

---

## 🛠️ Step-by-Step Recovery Process

If your computer crashes or you transition to a new laptop, follow these steps to restore your complete investing workspace and AI cognitive memory.

### **Step 1: Retrieve the Cloud Backup**
1.  Log into your **OneDrive** account on your web browser or sync client.
2.  Navigate to the backup folder:
    `OneDrive/Antigravity_Backups/`
3.  Identify the most recent backup archive (e.g., `Antigravity_Backup_YYYY-MM-DD_HHMMSS.zip`).
4.  Download the ZIP file to your local computer and extract its contents. You will find two directories inside the extracted folder:
    *   `Reports/`
    *   `AI_Brain/`

---

### **Step 2: Restore the Workspace Reports**
1.  Set up your workspace directory on the new machine:
    `d:\Projects\Antigravity\Financial AI\`
2.  Move the extracted **`Reports`** folder directly into the root workspace folder:
    👉 **`d:\Projects\Antigravity\Financial%20AI\Reports\`**
3.  Verify that your YYYY-MM daily subfolders and lists are present.

---

### **Step 3: Restore the AI Brain Memory (AppData)**
To restore the AI's cognitive ability and history, we must place the brain logs back into their standard Windows local AppData directory.

1.  Open Windows Explorer and navigate to your user profile directory:
    `C:\Users\<Your-Username>\`
2.  Create a folder chain named `.gemini\antigravity` if it doesn't already exist:
    `C:\Users\<Your-Username>\.gemini\antigravity`
3.  Copy all the contents of the extracted **`AI_Brain`** folder directly into:
    👉 **`C:\Users\<Your-Username>\.gemini\antigravity\`**
    
> [!IMPORTANT]
> Ensure that all folders like `brain/` and `knowledge/` are pasted directly inside `antigravity\`. This will restore all past conversation transcripts, portfolio balances, and risk parameters.

---

### **Step 4: Re-Register the Schedulers (New Machine Only)**
If this is a brand new computer, you must re-register the background automated tasks. Open a PowerShell terminal as Administrator, navigate to `d:\Projects\Antigravity\Financial AI\financial-services-plugins\etoro\scripts\`, and register your active schedulers:

1.  **Re-register the Weekly Workspace Backup**:
    Run this snippet in an Administrator PowerShell terminal to automatically register the backup scheduled task:
    ```powershell
    $WorkingDirectory = "d:\Projects\Antigravity\Financial AI"
    $ScriptPath = Join-Path $WorkingDirectory "backup_workspace.py"
    $PythonPath = (Get-Command python).Source
    $action = New-ScheduledTaskAction -Execute $PythonPath -Argument "`"$ScriptPath`"" -WorkingDirectory $WorkingDirectory
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At 6:00pm
    Register-ScheduledTask -TaskName "Antigravity_Workspace_Backup" -Action $action -Trigger $trigger -Description "Automated cloud backup of daily strategy Reports and AI memory" -Force
    ```
2.  **Re-register the Regulatory News Monitor**:
    ```powershell
    # Daily Vistra/eVTOL SEC monitoring at 8 AM and 5 PM:
    powershell -File reg_monitor_scheduler.ps1
    ```
3.  **Re-register the Dividend Reinvestment Engine (DRIP)**:
    ```powershell
    # Automated eToro cash balance sweeps every 4 hours:
    powershell -File drip_scheduler.ps1
    ```

---

## 🔒 Verification & Handshake Check

Once the restoration steps are complete, run a diagnostic handshake to confirm that the AI has successfully loaded your history and active portfolio status:

1.  Open the workspace in your IDE.
2.  Ask the AI: **"Fetch my portfolio and check if the strategy is working."**
3.  If the AI successfully reads your live open positions and maps them against your historical re-entry goals (like Silver executed at $74.47), **your restoration is 100% complete and fully verified!**
