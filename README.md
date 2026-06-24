# L2 Report Dashboard - Complete Setup & Usage Guide

## Overview

This project automatically generates an L2 Project Dashboard report from Excel files in your Box folder and sends it via email using Outlook.

**Status**: ✅ PRODUCTION READY

---

## Quick Start

### Manual Email Trigger
```powershell
cd "c:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB"
python send_l2_report_outlook_account.py
```

### Generate Report Only
```powershell
python generate_L2_report.py
```

---

## System Architecture

```
┌─────────────────────────────────────────────┐
│  Box Folder (L1 Report Repository)          │
│  └─ 8 Excel files (.xlsx, .xls, .xlsm)     │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  generate_L2_report.py                      │
│  ├─ Reads all Excel files                   │
│  ├─ Extracts project data                   │
│  ├─ Deduplicates by date                    │
│  └─ Generates HTML report                   │
└────────────────┬────────────────────────────┘
                 │
                 ▼
         html_reports/
         L2_Report.html
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  send_l2_report_outlook_account.py          │
│  ├─ Reads HTML report                       │
│  ├─ Creates email via Outlook               │
│  └─ Sends to recipients                     │
└────────────────┬────────────────────────────┘
                 │
                 ▼
      ┌──────────────────────┐
      │  Email Sent to:      │
      │  - lalvishn@ibm.com  │
      │  - lv1087@att.com    │
      └──────────────────────┘
```

---

## File Structure

```
Project Dashboard-L2 SQL DB/
├── generate_L2_report.py          # Report generator
├── send_l2_report_outlook_account.py   # Email sender
├── run_l2_report.bat              # Task scheduler wrapper
├── fix_task_scheduler.ps1         # Fix scheduler task
├── .env                           # Configuration
├── CONFIGURATION.md               # How to customize settings
├── README.md                      # This file
│
├── logs/                          # Daily execution logs
│   ├── email_delivery_20260624.log
│   ├── report_20260623_145700.log
│   └── validation_20260623_145633.log
│
└── html_reports/                  # Generated reports
    └── L2_Report.html
```

---

## Configuration

### Email Settings (`.env` file)

```env
# Recipients
EMAIL_FROM=lalvishn@in.ibm.com
EMAIL_TO=lalvishn@in.ibm.com,lv1087@att.com

# Email subject line
EMAIL_SUBJECT=L2 Project Dashboard Report - ETE Status Update

# Scheduled execution (24-hour format)
SCHEDULER_HOUR=0
SCHEDULER_MINUTE=0

# Source data folder
BOX_FOLDER_PATH=C:\Users\LalithVishnu\Box\L1 Report Repository
```

### Email Body Customization

To customize email messages, headers, footer, or signature, see [CONFIGURATION.md](CONFIGURATION.md)

---

## Data Source

**Location**: `C:\Users\LalithVishnu\Box\L1 Report Repository`

**Files Processed**: 8 Excel files
1. PID 437318 - ADIVB_Missing_Port
2. PID_437332 - SAREA
3. PID_437600 - DD NIS
4. PID_437501 - Wavelength Cycle Time
5. PID 437414 - AIAB ABV VC 763 (BC Flow)
6. PID 437491 - LISA 288.3
7. PID_437332 - ASEoD Deprecation Phase 2B
8. PID_437501 - CGW453_with_ABF_DD

**Supported Formats**: `.xlsx`, `.xls`, `.xlsm`

---

## Report Contents

The generated HTML report includes:

| Column | Source | Purpose |
|--------|--------|---------|
| Project ID | Filename (PID_XXXXX) | Unique project identifier |
| UFD # | Excel metadata (row 3-11, col 1) | Work item/ticket reference |
| Project Name | Filename (after PID) | Display name |
| Test Lead | Excel metadata (row 3-11, col 3-4) | Project test contact |
| Test Manager | Excel metadata (row 3-11, col 3-4) | Project manager |
| Plan Start | Excel "Overall Project Status" table | Planned start date |
| Plan End | Excel "Overall Project Status" table | Planned end date |
| Planned % | Excel "Overall Project Status" table | Planned completion %  |
| Passed % | Excel "Overall Project Status" table | Test passed % |
| Last Updated | Excel file modification time | Date of latest info |
| Overall Status | Excel "Overall Project Status" table | Current project status |

---

## Scheduling

### Daily Execution

The report is scheduled to run daily at **12:00 AM (00:00)**.

### Manual Trigger Anytime

```powershell
python send_l2_report_outlook_account.py
```

### Modify Schedule

**Option 1**: Edit `.env` file
```env
SCHEDULER_HOUR=8      # 8:00 AM
SCHEDULER_MINUTE=0
```

**Option 2**: Run PowerShell script (requires Admin)
```powershell
# Run as Administrator
cd "c:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB"
.\fix_task_scheduler.ps1
```

---

## Logging

All operations are logged to the `logs/` folder:

### Email Delivery Log
- **File**: `logs/email_delivery_YYYYMMDD.log`
- **Contains**: Email sending status, recipient info, errors
- **Updated**: Every time email is sent

### Example Log Entries
```
2026-06-24 00:08:33,214 - INFO - MANUAL EMAIL TRIGGER at 2026-06-24 00:08:33
2026-06-24 00:08:34,480 - INFO - [OK] L2_Report.html generated successfully
2026-06-24 00:08:41,249 - INFO - [OK] EMAIL SENT SUCCESSFULLY VIA OUTLOOK!
2026-06-24 00:08:42,299 - INFO - [OK] Timestamp: 2026-06-24 00:08:42
```

---

## Troubleshooting

### Issue: Email not sent at scheduled time

**Solution**: Run the fix script with Admin privileges
```powershell
# Right-click PowerShell and select "Run as Administrator"
cd "c:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB"
.\fix_task_scheduler.ps1
```

### Issue: Report shows only some projects

**Check**: Are all Excel files in the Box folder?
```powershell
dir "C:\Users\LalithVishnu\Box\L1 Report Repository" /b *.xlsx *.xls *.xlsm
```

### Issue: Outlook not found

**Solution**: Ensure Outlook is installed and running
- Outlook must be installed on the machine
- Can run with or without Outlook open (script will open if needed)

### Issue: File permission errors

**Solution**: Verify folder permissions
- `logs/` folder must be writable
- `html_reports/` folder must be writable
- `.env` file must be readable

---

## Code Components

### generate_L2_report.py

**Purpose**: Reads Excel files and generates HTML report

**Key Functions**:
- `extract_date_from_filename()` - Parses 5+ date formats from filenames
- `parse_project_info_from_filename()` - Extracts project ID and name (handles 4+ formats)
- `read_l2_project_data()` - Reads Excel metadata and status
- `deduplicate_by_project_name()` - Keeps only latest file per project
- `generate_l2_report_html()` - Creates email-ready HTML

**Output**: `html_reports/L2_Report.html`

### send_l2_report_outlook_account.py

**Purpose**: Sends generated report via Outlook email

**Key Functions**:
- `generate_l2_report()` - Calls generate_L2_report.py
- `send_via_outlook_account()` - Creates and sends email via Outlook COM objects
- `send_l2_report_email()` - Main orchestration function

**Logging**: Saves to `logs/email_delivery_YYYYMMDD.log`

---

## Technology Stack

- **Python 3.11.9**
- **Libraries**:
  - `pandas` - Excel file reading
  - `openpyxl` - Excel worksheet access
  - `win32com` - Outlook automation
  - `python-dotenv` - Configuration management
- **Email**: Outlook MAPI (no SMTP credentials needed)
- **Scheduler**: Windows Task Scheduler

---

## Maintenance

### Monthly Tasks
- Review logs in `logs/` folder for any errors
- Verify email recipients are still valid in `.env`

### When New Projects Arrive
- Place new Excel files in Box folder with proper naming
- Automatic execution next day at midnight
- No configuration changes needed

### When Moving System
1. Update paths in `.env` (if folder location changes)
2. Reinstall Python dependencies: `pip install -r requirements.txt`
3. Run scheduler fix script: `.\fix_task_scheduler.ps1` (as Admin)

---

## Support & Documentation

- **Configuration Details**: See [CONFIGURATION.md](CONFIGURATION.md)
- **Email Customization**: Edit messages in [CONFIGURATION.md](CONFIGURATION.md)
- **Schedule Changes**: Use `.env` file or `fix_task_scheduler.ps1`
- **Logs Location**: `logs/` folder (daily dated files)
- **Report Location**: `html_reports/L2_Report.html`

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-06-24 | 2.0 | Reorganized folders (logs/, html_reports/), Added CONFIGURATION.md, Fixed task scheduler path |
| 2026-06-23 | 1.5 | Added .xlsm support, Enhanced filename parsing |
| Earlier | 1.0 | Initial version |

---

## Last Updated
2026-06-24 00:08:42

**Status**: All systems operational ✅

---

## Quick Reference

| Action | Command |
|--------|---------|
| Generate report | `python generate_L2_report.py` |
| Send email manually | `python send_l2_report_outlook_account.py` |
| View latest log | `Get-Content logs/email_delivery_*.log -Tail 20` |
| View latest report | `Start-Process html_reports/L2_Report.html` |
| Fix scheduler (Admin) | `.\fix_task_scheduler.ps1` |
| Check task status | `Get-ScheduledTask -TaskName 'L2 Project Dashboard Report'` |

