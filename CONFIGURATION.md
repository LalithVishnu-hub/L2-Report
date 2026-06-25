# L2 Report Dashboard - Configuration Guide

This file allows you to customize all email settings, messages, and report formatting without editing Python code.

## Email Configuration

### Email Recipients
Edit these values in `.env` file or below:
- **EMAIL_FROM**: `lalvishn@in.ibm.com` → Your email address sending the report
- **EMAIL_TO**: `lalvishn@in.ibm.com,lv1087@att.com` → Recipients (comma-separated)

### Email Subject Line
```
EMAIL_SUBJECT=L2 Project Dashboard Report - ETE Status Update
```
Optional alias (if you prefer the word "submit"):
```
EMAIL_SUBMIT=L2 Project Dashboard Report - ETE Status Update
```
**Customize to:** Any subject line you prefer
- Example 1: `L2 Daily Report - Project Status`
- Example 2: `ETE Project Dashboard - Daily Update`
- Example 3: `Project Status Summary Report`

### Editable Greeting, Intro, Footer, Signature (No code changes)
Set these in `.env`:
```env
EMAIL_GREETING=Hi All,
EMAIL_INTRO_MESSAGE=Please find below the L2 Project Dashboard for ETE Wireline Projects.
EMAIL_FOOTER=This report is automatically generated and sent daily. For any questions or clarifications regarding the projects listed above, please reach out to the respective Test Lead or Test Manager.
EMAIL_SIGNATURE=Thanks & Regards,\nLalith Vishnu. S
```
Notes:
- `\n` in `EMAIL_SIGNATURE` is rendered as a new line in the email.
- These values are inserted into the generated HTML report.

---

## Email Body Customization

### Paragraph Message (Before Table)
**Current location in code:** `generate_L2_report.py` → `get_email_body()` function

**Current text:**
```html
<p style="margin: 15px 0; font-family: Arial, sans-serif; font-size: 14px; color: #333;">
    Below is the current status of all L2 projects with their ETE (End-to-End) completion status.
    Please review the latest updates and reach out to project leads for any clarifications.
</p>
```

**To customize:**
1. Open `generate_L2_report.py`
2. Find the `get_email_body()` function
3. Locate the first `<p>` tag with the opening message
4. Edit the text between the tags (keep the HTML styling)

**Examples of custom messages:**
- "Please find below the latest ETE status for all active L2 projects. Contact project teams for updates."
- "Current L2 Project Dashboard update as of today. Review status and escalate any blockers."
- "Attached is your daily L2 project status report. All timestamps reflect the latest available data."

---

## Table Header Customization

**Current column headers:**
| Column | Current Name | Purpose |
|--------|--------------|---------|
| 1 | Project Name | Display name of the project |
| 2 | PID | Project ID number |
| 3 | UFD# | Work item/ticket reference |
| 4 | Last Updated | Date of latest information |
| 5 | Status | Project status value |

**To customize headers:**
1. Open `generate_L2_report.py`
2. Find the `generate_html_report()` function
3. Locate the `<tr>` section with `<th>` tags
4. Edit header text inside the `<th>` tags

**Example custom headers:**
```html
<th style="width: 25%; background-color: #004B87; color: white; padding: 12px;">Project Title</th>
<th style="width: 15%; background-color: #004B87; color: white; padding: 12px;">Project Code</th>
<th style="width: 20%; background-color: #004B87; color: white; padding: 12px;">Task ID</th>
<th style="width: 20%; background-color: #004B87; color: white; padding: 12px;">Updated On</th>
<th style="width: 20%; background-color: #004B87; color: white; padding: 12px;">Current Status</th>
```

---

## Footer Message Customization

**Current location in code:** `generate_L2_report.py` → `get_email_body()` function

**Current text:**
```html
<p style="margin: 20px 0 0 0; font-family: Arial, sans-serif; font-size: 12px; color: #666; border-top: 1px solid #ddd; padding-top: 15px;">
    <strong>Automated Report:</strong> This report is generated daily at 12:00 AM (midnight) and includes all projects 
    from the L1 Report Repository. For questions or issues, please contact the report administrator.
</p>
```

**To customize:**
1. Open `generate_L2_report.py`
2. Find the `get_email_body()` function
3. Locate the last `<p>` tag (footer section)
4. Edit text between the tags

**Example custom footers:**
- "This is an automated daily report. Contact: lalvishn@in.ibm.com for support."
- "Report generated automatically. Data refreshed daily. Questions? Email L2-Reports@company.com"
- "For report issues or data clarifications, please reach out to the L2 Dashboard team."

---

## Signature Customization

**Current location in code:** `generate_L2_report.py` → `get_email_body()` function

**Current text:**
```html
<p style="margin: 15px 0 0 0; font-family: Arial, sans-serif; font-size: 12px; color: #333;">
    Best regards,<br>
    <strong>L2 Project Dashboard</strong><br>
    Automated Report System
</p>
```

**To customize:**
1. Open `generate_L2_report.py`
2. Find the `get_email_body()` function
3. Locate the signature section (after the footer)
4. Edit the text and name

**Example custom signatures:**
```html
<!-- Option 1: Department-based -->
<p style="margin: 15px 0 0 0; font-family: Arial, sans-serif; font-size: 12px; color: #333;">
    Best regards,<br>
    <strong>L2 Project Management Team</strong><br>
    Project Operations
</p>

<!-- Option 2: Personal -->
<p style="margin: 15px 0 0 0; font-family: Arial, sans-serif; font-size: 12px; color: #333;">
    Thank you,<br>
    <strong>Lalith Vishnu</strong><br>
    Project Dashboard Administrator
</p>

<!-- Option 3: Brief -->
<p style="margin: 15px 0 0 0; font-family: Arial, sans-serif; font-size: 12px; color: #333;">
    Dashboard Report System
</p>
```

---

## Scheduling Configuration

### Daily Execution Time
**Current setting:** 12:00 AM (00:00) every day

**To change:**
1. Edit `.env` file:
   ```
   SCHEDULER_HOUR=0
   SCHEDULER_MINUTE=0
   ```
2. Set desired time (24-hour format):
   - `SCHEDULER_HOUR=8` and `SCHEDULER_MINUTE=0` → 8:00 AM
   - `SCHEDULER_HOUR=14` and `SCHEDULER_MINUTE=30` → 2:30 PM
   - `SCHEDULER_HOUR=23` and `SCHEDULER_MINUTE=59` → 11:59 PM

3. Restart the scheduler

### Important Scheduler Behavior (Windows Task Scheduler)
- Sleep mode: Supported via wake timers + task `WakeToRun`.
- Shutdown/off: Exact-time execution is not possible on a powered-off local PC.
- If exact-time execution while PC is off is mandatory, use GitHub Actions scheduler (`.github/workflows/l2-report-daily.yml`).

---

## Output Files Location

| File | Location | Purpose |
|------|----------|---------|
| **L2_Report.html** | `html_reports/` | Generated report HTML (latest) |
| **Scheduler Log** | `logs/` | Daily execution logs |
| **Email Delivery Log** | `logs/` | Email sending logs with timestamps |

---

## How to Edit Configuration

### Option 1: Direct Edit (Python Code)
1. Open `generate_L2_report.py`
2. Find the function containing text you want to change
3. Modify the text inside HTML tags
4. Save the file
5. Run: `python send_l2_report_outlook_account.py` to test

### Option 2: Automated Script
Run this PowerShell command to generate a fresh report:
```powershell
cd "c:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB"
python generate_L2_report.py
```

---

## Quick Reference

| Setting | File | Location | Example |
|---------|------|----------|---------|
| Email recipients | `.env` | `EMAIL_TO=` | `user1@email.com,user2@email.com` |
| Email subject | `.env` | `EMAIL_SUBJECT=` | `L2 Daily Report` |
| Report title | `generate_L2_report.py` | `get_email_body()` | Edit HTML `<h1>` tag |
| Message content | `generate_L2_report.py` | `get_email_body()` | Edit `<p>` tags |
| Column headers | `generate_L2_report.py` | `generate_html_report()` | Edit `<th>` tags |
| Footer text | `generate_L2_report.py` | `get_email_body()` | Edit footer `<p>` tag |
| Signature | `generate_L2_report.py` | `get_email_body()` | Edit signature `<p>` tag |
| Schedule time | `.env` | `SCHEDULER_HOUR=` `SCHEDULER_MINUTE=` | `8` and `0` for 8 AM |

---

## Testing Changes

After making any changes:

```powershell
# Test report generation
python generate_L2_report.py

# Test email sending
python send_l2_report_outlook_account.py

# Check logs
Get-Content logs/*.log -Tail 20
```

---

## Environment Variables (.env)

```env
# Email Configuration
EMAIL_FROM=lalvishn@in.ibm.com
EMAIL_TO=lalvishn@in.ibm.com,lv1087@att.com
EMAIL_SUBJECT=L2 Project Dashboard Report - ETE Status Update

# Schedule (24-hour format)
SCHEDULER_HOUR=0
SCHEDULER_MINUTE=0

# Box Folder Path
BOX_FOLDER_PATH=C:\Users\LalithVishnu\Box\L1 Report Repository
```

