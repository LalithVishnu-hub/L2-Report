# L2 Report Scheduler - Setup Instructions (12:30 AM)

## ✅ What Was Done

### 1. Cleanup (27 old files removed)
- Removed outdated documentation and setup scripts
- Reduced from 46 files to 16 files in main directory
- Cleaner, production-ready workspace

### 2. Organized L2 Report Email
- ✅ Created new folder: `L2_Report_Mail/`
- ✅ Moved `send_l2_report_outlook_account.py` to `L2_Report_Mail/`
- ✅ Updated paths to reference parent directory
- ✅ Updated `run_l2_report.bat` to call script from new folder

### 3. Updated Task Scheduler Script
- ✅ Changed schedule time to **12:30 AM** (00:30:00)
- ✅ Added error handling and status reporting
- ✅ Added admin privilege verification
- ✅ Updated `fix_task_scheduler.ps1` with detailed logging

### 4. Created Elevated Execution Helper
- ✅ New file: `setup_scheduler_elevated.bat`
- ✅ Automatically requests admin privileges
- ✅ Handles elevation cleanly

---

## 📁 New Directory Structure

```
Project Dashboard-L2 SQL DB/
├── Core Files (16)
│   ├── generate_L2_report.py          [Report generator]
│   ├── run_l2_report.bat              [Task wrapper]
│   ├── .env                           [Configuration]
│   ├── README.md, CONFIGURATION.md    [Documentation]
│   └── ...more documentation
│
├── L2_Report_Mail/                    [NEW - Email management]
│   ├── send_l2_report_outlook_account.py
│   └── (handles email delivery)
│
├── logs/                              [Daily logs]
│   └── email_delivery_*.log
│
├── html_reports/                      [Generated reports]
│   └── L2_Report.html
│
└── Other folders
    └── (dashboard, static, etc.)
```

---

## 🚀 How to Enable Scheduled Email at 12:30 AM

### Option 1: Recommended (Easiest)
```
1. Open File Explorer
2. Navigate to: C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB
3. Right-click on: setup_scheduler_elevated.bat
4. Select: "Run as administrator"
5. Click "Yes" when prompted
6. Wait for completion message
```

### Option 2: Using Command Line (Admin)
```powershell
# Open PowerShell as Administrator
# Then run:

cd "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB"
.\fix_task_scheduler.ps1
```

### Option 3: Using Batch File
```
1. Open Command Prompt as Administrator
2. Navigate to project folder
3. Run: run_fix_task_scheduler.bat
```

---

## ✅ Testing After Setup

### Verify Task Created
```powershell
Get-ScheduledTask -TaskName "L2 Project Dashboard Report" | Get-ScheduledTaskInfo
```

**Expected Output:**
```
NextRunTime    : 25-06-2026 00:30:00
LastRunTime    : 24-06-2026 00:08:42
LastTaskResult : 0
```

### Manual Test (Anytime)
```powershell
cd "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB"
python L2_Report_Mail\send_l2_report_outlook_account.py
```

**Expected Output:**
```
[OK] EMAIL SENT SUCCESSFULLY VIA OUTLOOK!
```

---

## 📝 Schedule Details

| Setting | Value |
|---------|-------|
| **Task Name** | L2 Project Dashboard Report |
| **Schedule** | Daily |
| **Time** | 12:30 AM (00:30:00) |
| **Start When Available** | Yes (if system is asleep) |
| **Network Required** | Yes |
| **Run Level** | Highest (Admin) |

---

## 📊 File Organization Summary

### Removed (27 files)
- Old setup guides
- Legacy implementations
- Test/debug artifacts
- Outdated documentation

### Kept (16 files)
- Production code
- Configuration
- Essential documentation
- Execution wrappers

### New Structures
- `L2_Report_Mail/` folder for email logic
- `logs/` folder for execution history
- `html_reports/` folder for generated reports

---

## ⚙️ How It Works Now

```
Daily at 12:30 AM:
  ↓
Task Scheduler runs: run_l2_report.bat
  ↓
Batch file navigates to main directory
  ↓
Calls: python L2_Report_Mail\send_l2_report_outlook_account.py
  ↓
Script generates report from Excel files
  ↓
Script sends email via Outlook
  ↓
Logs result to: logs/email_delivery_YYYYMMDD.log
```

---

## 🔧 Configuration

### Email Recipients
Edit `.env`:
```env
EMAIL_TO=lalvishn@in.ibm.com,lv1087@att.com
```

### Email Subject
Edit `.env`:
```env
EMAIL_SUBJECT=L2 Project Dashboard Report - ETE Status Update
```

### Schedule Time
To change from 12:30 AM:
1. Edit `fix_task_scheduler.ps1`
2. Find line: `-At 00:30:00`
3. Change to desired time (24-hour format)
4. Run the script again

---

## 📋 Troubleshooting

### Task Not Running?
1. Check if script ran with admin privileges
2. Run `Get-ScheduledTask` to verify task exists
3. Check `logs/email_delivery_*.log` for errors
4. Re-run the setup script

### Email Not Sending?
1. Verify Outlook is installed
2. Check `.env` for correct email addresses
3. Run manual test: `python L2_Report_Mail\send_l2_report_outlook_account.py`
4. Check logs for specific error message

### Path Not Found?
1. Verify batch file paths are correct
2. Ensure all folders exist (logs/, html_reports/, L2_Report_Mail/)
3. Re-run setup if needed

---

## ✅ After Setup Complete

1. ✅ Email will send daily at 12:30 AM automatically
2. ✅ All operations logged to `logs/` folder
3. ✅ Reports saved to `html_reports/` folder
4. ✅ Can manually send anytime: `python L2_Report_Mail\send_l2_report_outlook_account.py`
5. ✅ Clean, organized file structure

---

## 📞 Quick Commands

```powershell
# Check task status
Get-ScheduledTask -TaskName "L2 Project Dashboard Report" | Get-ScheduledTaskInfo

# View latest log
Get-Content logs/email_delivery_*.log -Tail 30

# Manual email send
python L2_Report_Mail\send_l2_report_outlook_account.py

# View latest report
Start-Process html_reports/L2_Report.html
```

---

## 🎯 Next Steps

1. **RIGHT NOW**: Run `setup_scheduler_elevated.bat` (or use Option 2/3 above)
2. **VERIFY**: Check task created with: `Get-ScheduledTask -TaskName "L2 Project Dashboard Report"`
3. **CONFIRM**: Check that `NextRunTime` shows tomorrow at 00:30:00
4. **DONE**: System will send email automatically daily at 12:30 AM

---

**Status**: Ready for scheduler setup
**Schedule Time**: 12:30 AM (00:30:00) daily
**Last Updated**: 2026-06-24

