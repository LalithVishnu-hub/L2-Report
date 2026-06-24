# 📧 L2_Report_Mail Folder - Complete L2 Report & Email System

## 📋 Overview

The `L2_Report_Mail` folder contains **ALL files related to generating and sending the L2 Project Dashboard report**. This folder is completely self-contained and can be run independently.

---

## 📁 Folder Contents

```
L2_Report_Mail/
├── Core Report Generation
│   ├── generate_L2_report.py           # Reads Excel files & generates HTML report
│   └── send_l2_report_outlook_account.py   # Sends email via Outlook MAPI
│
├── Batch Wrappers
│   ├── run_l2_report.bat               # Task Scheduler execution wrapper
│   └── run_fix_task_scheduler.bat      # Alternative scheduler runner
│
├── Scheduler Setup Scripts
│   ├── fix_task_scheduler.ps1          # Main PowerShell setup script (run as admin)
│   ├── setup_scheduler_elevated.bat    # Auto-elevates for admin privileges
│   ├── setup_task_scheduler.py         # Python scheduler setup
│   └── create_task_scheduler.py        # Alternative Python setup
│
└── __pycache__/                        # Python cache (auto-generated)
```

---

## 🚀 How to Use

### Option 1: Manual Email Trigger (Anytime)
```powershell
cd "L2_Report_Mail"
python send_l2_report_outlook_account.py
```

### Option 2: Run via Batch Wrapper
```cmd
cd "L2_Report_Mail"
run_l2_report.bat
```

### Option 3: Setup Daily Automation at 12:30 AM
```powershell
cd "L2_Report_Mail"
.\setup_scheduler_elevated.bat    # Right-click → Run as administrator
```

---

## 📊 File Details

| File | Purpose | Type |
|------|---------|------|
| `generate_L2_report.py` | Reads 9 Excel files from Box, generates HTML report | Python |
| `send_l2_report_outlook_account.py` | Sends HTML report email via Outlook | Python |
| `run_l2_report.bat` | Batch wrapper for Task Scheduler | Batch |
| `fix_task_scheduler.ps1` | Creates/updates Windows Task Scheduler task | PowerShell |
| `setup_scheduler_elevated.bat` | Auto-elevates PowerShell for admin | Batch |
| `setup_task_scheduler.py` | Alternative Python-based scheduler setup | Python |
| `create_task_scheduler.py` | Alternative task creation method | Python |

---

## ⚙️ Configuration

Configuration is managed via the **`.env` file in the parent directory**:

```env
EMAIL_FROM=lalvishn@in.ibm.com
EMAIL_TO=lalvishn@in.ibm.com,lv1087@att.com
EMAIL_SUBJECT=L2 Project Dashboard Report - ETE Status Update
SCHEDULER_HOUR=0
SCHEDULER_MINUTE=30
BOX_FOLDER_PATH=C:\Users\LalithVishnu\Box\L1 Report Repository
```

**To modify settings:**
1. Edit `.env` file in parent directory
2. Changes take effect on next email send
3. No restart needed

---

## 📤 Output Locations

| Output | Location | Created By |
|--------|----------|-----------|
| **HTML Report** | `../html_reports/L2_Report.html` | `generate_L2_report.py` |
| **Logs** | `../logs/email_delivery_YYYYMMDD.log` | `send_l2_report_outlook_account.py` |

---

## 🔄 Daily Automation Flow

```
Windows Task Scheduler (12:30 AM Daily)
        ↓
    run_l2_report.bat
        ↓
    send_l2_report_outlook_account.py
        ↓
    Calls: generate_L2_report.py
        ├─ Reads: C:\Users\LalithVishnu\Box\L1 Report Repository (9 Excel files)
        ├─ Generates: ../html_reports/L2_Report.html
        └─ Returns: Success/Failure
        ↓
    Sends Email (via Outlook MAPI)
        ├─ Recipients: lalvishn@in.ibm.com, lv1087@att.com
        ├─ Subject: L2 Project Dashboard Report - ETE Status Update
        └─ Body: HTML report
        ↓
    Logs Result: ../logs/email_delivery_YYYYMMDD.log
```

---

## 💡 Key Features

✅ **Self-Contained**: All L2 report/email files in one folder  
✅ **No SMTP Credentials Needed**: Uses Outlook COM objects  
✅ **Automated Daily**: Runs at 12:30 AM via Windows Task Scheduler  
✅ **Manual Trigger**: Can run anytime with Python script  
✅ **Comprehensive Logging**: Full execution trace in logs/  
✅ **Error Handling**: Automatic retries for Outlook connection  
✅ **Deduplication**: Keeps latest file version by date  
✅ **Multiple Date Formats**: Supports 5+ filename date formats  

---

## 🔧 Quick Commands

### Check Task Status
```powershell
Get-ScheduledTask -TaskName "L2 Project Dashboard Report" | Get-ScheduledTaskInfo
```

### Manual Email Test
```powershell
python send_l2_report_outlook_account.py
```

### View Latest Logs
```powershell
Get-Content ..\logs\email_delivery_*.log | Select-Object -Last 30
```

### Disable/Enable Automation
```powershell
# Disable
Disable-ScheduledTask -TaskName "L2 Project Dashboard Report"

# Enable
Enable-ScheduledTask -TaskName "L2 Project Dashboard Report"
```

### Remove Task (If needed)
```powershell
Unregister-ScheduledTask -TaskName "L2 Project Dashboard Report"
```

---

## 📝 Last Test Results

| Test | Status | Time |
|------|--------|------|
| Email Send | ✅ SUCCESS | 2026-06-24 00:25:29 |
| Report Generation | ✅ SUCCESS | 9 projects processed |
| All 9 Excel Files | ✅ PROCESSED | All found and parsed |
| Recipient Resolution | ✅ SUCCESS | Both recipients resolved |
| Outlook Connection | ✅ SUCCESS | Account: lalvishn@in.ibm.com |

---

## 📞 Support

### Problem: "Could not parse project ID"
- **Solution**: Check Excel filename format matches one of these patterns:
  - `PID_XXXXX_ProjectName_...xlsx`
  - `PID XXXXX ProjectName ...xlsx`
  - `XXXXX_ProjectName_...xlsx`

### Problem: "No recipients found"
- **Solution**: Check `.env` file EMAIL_TO variable is set correctly
- Format: `email1@domain.com,email2@domain.com` (comma-separated, no spaces)

### Problem: "Outlook not found"
- **Solution**: Install Outlook or check Windows COM objects are available
- The system will attempt to start Outlook automatically if not running

### Problem: "Task not running at 12:30 AM"
- **Solution**: Run `setup_scheduler_elevated.bat` as administrator again
- Verify with: `Get-ScheduledTask -TaskName "L2 Project Dashboard Report" | Get-ScheduledTaskInfo`

---

## 🎯 Next Steps

1. ✅ All files consolidated in L2_Report_Mail folder
2. ✅ Manual email tested and working
3. ⏳ **Setup automation**: Run `setup_scheduler_elevated.bat` (right-click → Admin)
4. 📅 **Tomorrow 12:30 AM**: First automated email delivery
5. 📊 **Monitor**: Check `../logs/email_delivery_*.log` for results

---

## ✨ System Status

```
┌────────────────────────────────────────┐
│     L2_Report_Mail System Status       │
├────────────────────────────────────────┤
│  Organization:        ✅ COMPLETE      │
│  File Consolidation:  ✅ COMPLETE      │
│  Manual Test:         ✅ SUCCESS       │
│  Path Updates:        ✅ COMPLETE      │
│  Configuration:       ✅ READY         │
│  Automation Setup:    ⏳ PENDING       │
│  Daily Emails:        🔄 SCHEDULED     │
└────────────────────────────────────────┘
```

---

**Created**: 2026-06-24  
**Last Updated**: 2026-06-24 00:25:29  
**Status**: ✅ Production Ready
