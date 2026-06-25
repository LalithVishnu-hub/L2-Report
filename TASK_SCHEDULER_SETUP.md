# Task Scheduler Setup - Automated Configuration

## Quick Start (Administrator PowerShell)

```powershell
# Right-click PowerShell → "Run as Administrator" → Paste this:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
& "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\setup_task_scheduler.ps1"
```

The script will:
✅ Create/update the L2 Report Daily task
✅ Set it to run at 4:00 PM every day
✅ Allow it to run when PC is locked
✅ Allow it to run on battery
✅ Retry if it fails
✅ Run with highest privileges

---

## What The Script Does

1. **Creates task** named "L2 Report Daily" in "\L2 Report\" folder
2. **Sets trigger** for daily at 4:00 PM
3. **Configures settings:**
   - ✅ "Run whether user is logged in or not"
   - ✅ "Run with highest privileges"
   - ✅ "Start when available" (runs even if PC was off at 4 PM)
   - ✅ "Allow start on battery"
   - ✅ "Don't stop on battery"
   - ✅ Network available check
4. **Uses your Python venv** to run the script

---

## Verification

After running the script:

1. **Open Task Scheduler:**
   - Press `Windows Key + R` → Type `taskscheduler.msc` → Press Enter

2. **Find the task:**
   - Navigate to: **Task Scheduler Library** → **L2 Report** folder
   - Should see: **L2 Report Daily**

3. **Verify settings:**
   - Right-click task → **Properties**
   - **General tab:**
     - ✓ "Run whether user is logged in or not" - CHECKED
     - ✓ "Run with highest privileges" - CHECKED
   - **Conditions tab:**
     - ☐ "Start the task only if the computer is on AC power" - UNCHECKED
     - ☐ "Wake the computer to run this task" - UNCHECKED (optional)
   - **Settings tab:**
     - ✓ "Allow task to be run on demand" - CHECKED
     - ✓ "Run task as soon as possible if a scheduled start is missed" - CHECKED
     - ✓ "If the task fails, restart every: 1 minute" - SET

---

## Test the Task

### Test 1: Manual Trigger
1. Open Task Scheduler
2. Right-click **L2 Report Daily** → **Run**
3. Check if it completes (should be quick)
4. Verify email was sent to `lv1087@att.com`

### Test 2: Check Logs
```bash
cd "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\logs"
ls -la  # List all log files
tail -f email_delivery_*.log  # View latest log
```

### Test 3: Verify When PC is Locked
1. Schedule task to run in 1 minute (edit in Task Scheduler)
2. Lock your PC: **Windows Key + L**
3. Wait for task to execute
4. Check logs to confirm it ran while locked

---

## Troubleshooting

### Script won't run as Administrator?
```powershell
# Try this instead:
Start-Process PowerShell -Verb RunAs
# Then paste the script command
```

### Task doesn't appear in Task Scheduler?
- Refresh: Press **F5** in Task Scheduler
- Restart Task Scheduler: 
  ```powershell
  Stop-Service Schedule
  Start-Service Schedule
  ```

### Task runs but email doesn't send?
1. Check logs: `C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\logs\`
2. Manually run: 
   ```bash
   cd "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB"
   .\.venv\Scripts\python.exe L2_Report_Mail\send_l2_report_outlook_account.py
   ```
3. Check if Outlook is installed and has your email configured

### "Access Denied" when creating task?
- Make sure you run PowerShell as **Administrator**
- Try: `sudo` command (Windows 11) or right-click → Run as Administrator

---

## Once Local Setup Works

After confirming the task runs successfully:

1. GitHub Actions will be re-enabled
2. When you push report to GitHub, it auto-sends email via GitHub too
3. You'll have backups in GitHub Actions tab

---

## Manual Run Command

If you need to run manually:
```bash
cd "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB"
.\.venv\Scripts\python.exe L2_Report_Mail\send_l2_report_outlook_account.py
```
