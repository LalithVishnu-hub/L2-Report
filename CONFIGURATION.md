# 📋 Complete Configuration & Deployment Guide

## 🎯 Overview: Local vs Cloud Execution

Your L2 Report system has **TWO independent execution paths**:

| Feature | **LOCAL (Task Scheduler)** | **CLOUD (GitHub Actions)** |
|---------|--------------------------|-------------------------|
| **When it runs** | Only when your PC is ON | 24/7, always (even PC off) |
| **Scheduling** | Windows Task Scheduler | GitHub Actions Workflow |
| **Email send method** | Outlook COM (Windows) | SMTP (cloud-based) |
| **Configuration** | `.env` file (local) | GitHub Secrets (web) |
| **Best for** | Office environment | Always-on reporting |
| **Requirements** | Windows PC + Outlook | GitHub repository access |
| **Status** | ✅ Currently active | ✅ Currently configured |

---

## 🚨 IMPORTANT: Why You Need GitHub Actions

Your requirement: **"Trigger mail even when PC is shutdown"**

### ❌ Task Scheduler ALONE is NOT sufficient:
- Runs only when Windows is powered ON
- If PC sleeps/shuts down, scheduled time is missed
- No catch-up mechanism (StartWhenAvailable is disabled)

### ✅ GitHub Actions IS the solution:
- Runs on GitHub's servers (cloud infrastructure)
- Runs at exact scheduled time regardless of your PC status
- Independent from your local system
- **This is what you NEED for 24/7 reporting**

---

## 📖 Choose Your Setup

### **Setup A: Local Only (Office Environment)**
Use if: Your PC runs 24/7 or you only need reports during business hours
- Task Scheduler: ✅ YES
- GitHub Actions: ❌ NO

### **Setup B: Cloud Only (Recommended for Always-On)** ⭐
Use if: You need reports sent even at night/weekends when PC is off
- Task Scheduler: ❌ NO
- GitHub Actions: ✅ YES ⭐ **RECOMMENDED FOR YOUR CASE**

### **Setup C: Both (Redundancy)**
Use if: You want backup - if one fails, other still sends
- Task Scheduler: ✅ YES
- GitHub Actions: ✅ YES

---

# 🔧 SETUP INSTRUCTIONS

## Part 1: Common Configuration (Both Local & Cloud)

### Step 1️⃣: Edit `.env` File (Local Configuration)

File location: `C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\.env`

```env
# ==================== EMAIL CONFIGURATION ====================
EMAIL_FROM=lalvishn@in.ibm.com
EMAIL_TO=lv1087@att.com
EMAIL_SUBJECT=L2 Project Dashboard Report - ETE Status Update
EMAIL_GREETING=Hi All,
EMAIL_INTRO_MESSAGE=Please find below the L2 Project Dashboard for ETE Wireline Projects.
EMAIL_FOOTER=This report is automatically generated and sent daily. For any questions or concerns, please reach out to the test team.
EMAIL_SIGNATURE=Thanks & Regards,\nLalith Vishnu. S

# ==================== SCHEDULE CONFIGURATION ====================
SCHEDULER_HOUR=16
SCHEDULER_MINUTE=0

# ==================== DATA SOURCE ====================
BOX_LOCAL_PATH=C:\Users\LalithVishnu\Box\L1 Report Repository

# ==================== GITHUB PAGES ====================
GITHUB_PAGES_BASE_URL=https://lalithvishnu-hub.github.io/L2-Report
L1_DASHBOARD_BASE_URL=http://localhost:5000

# ==================== SMTP (Cloud/GitHub Actions) ====================
SMTP_SERVER=Outlook
SMTP_PORT=0
SMTP_USER=
SMTP_PASS=
SMTP_USE_TLS=false
SMTP_USE_AUTH=false

# ==================== GITHUB (for auto-push) ====================
GITHUB_TOKEN=github_pat_11B... (your token)
GITHUB_USER=LalithVishnu-hub
GITHUB_REPO=L2-Report
```

**Edit these values to customize your setup:**
- `EMAIL_FROM`: Your email address
- `EMAIL_TO`: Recipient(s) - use comma for multiple: `email1@company.com, email2@company.com`
- `EMAIL_SUBJECT`: Subject line of email
- `EMAIL_GREETING`: Email greeting (e.g., "Hi Team,")
- `EMAIL_INTRO_MESSAGE`: Opening message
- `EMAIL_FOOTER`: Closing message before signature
- `EMAIL_SIGNATURE`: Sign-off (use `\n` for line breaks)
- `SCHEDULER_HOUR`: Time to run (0-23, 24-hour format)
- `SCHEDULER_MINUTE`: Minutes (0-59)

**Notes:**
- ⚠️ `.env` is in `.gitignore` - NOT committed to GitHub
- ⚠️ Never share `GITHUB_TOKEN` value
- ✅ Changes take effect on next run

---

## Part 2: Local Setup (Task Scheduler)

### When to use: 
- Your PC runs 24/7
- You only need reports during business hours
- Your PC is reliably ON at scheduled time

### Step 2️⃣: Apply Schedule to Windows Task Scheduler

```powershell
# Open PowerShell as Administrator
# Navigate to project folder
cd "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB"

# Run the scheduler setup script
powershell -ExecutionPolicy Bypass -File "L2_Report_Mail\fix_task_scheduler.ps1"
```

**What this does:**
- Creates/updates Windows Task Scheduler task named `L2_Report_Daily_ETE`
- Sets schedule to time specified in `SCHEDULER_HOUR` and `SCHEDULER_MINUTE`
- Configures task to wake PC from sleep (`-WakeToRun $true`)
- Disables catch-up runs if PC was off (`-StartWhenAvailable $false`)
- Task runs: `L2_Report_Mail\run_l2_report.bat`

### Step 3️⃣: Verify Schedule

```powershell
# Check if task created successfully
Get-ScheduledTask -TaskName "L2_Report_Daily_ETE" | fl

# Expected output shows:
# TaskPath: \
# TaskName: L2_Report_Daily_ETE
# State: Ready
# Triggers: {Daily schedule at HH:MM}
```

### Step 4️⃣: Test Local Execution

```powershell
cd "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\L2_Report_Mail"

# Test Outlook email send
python send_l2_report_outlook_account.py

# Check: Email should arrive in next 30 seconds
# If yes: ✅ Local setup complete
```

### Step 5️⃣: What Happens on Schedule

When Task Scheduler runs at scheduled time (e.g., 4:00 PM):

```
1. Windows Task Scheduler triggers run_l2_report.bat
2. Batch file runs: send_l2_report_outlook_account.py
3. Python script:
   ✓ Reads Excel files from Box folder
   ✓ Generates L2_Report.html email body
   ✓ Generates L1 static pages (PID_XXXXX.html)
   ✓ Sends email via Outlook
   ✓ Logs to: logs/email_delivery_YYYYMMDD.log
4. Batch file git commits and pushes HTML reports
5. GitHub auto-deploys to GitHub Pages
6. Email + L1 pages live ✅
```

---

## Part 3: Cloud Setup (GitHub Actions) ⭐ RECOMMENDED

### When to use: ⭐ **RECOMMENDED**
- You need 24/7 reporting
- PC can be OFF, asleep, or unavailable
- Consistent schedule regardless of system state
- **THIS IS YOUR REQUIREMENT - "Trigger mail even when PC is shutdown"**

### Step 6️⃣: Create GitHub Actions Workflow

1. **Go to your GitHub repository:**
   - URL: `https://github.com/LalithVishnu-hub/L2-Report`
   - Click: **Settings** → **Secrets and variables** → **Actions**

2. **Add these Repository Secrets:**

   | Secret Name | Value | Source |
   |---|---|---|
   | `EMAIL_FROM` | `lalvishn@in.ibm.com` | Copy from `.env` |
   | `EMAIL_TO` | `lv1087@att.com` | Copy from `.env` |
   | `EMAIL_SUBJECT` | `L2 Project Dashboard Report - ETE Status Update` | Copy from `.env` |
   | `EMAIL_GREETING` | `Hi All,` | Copy from `.env` |
   | `EMAIL_INTRO_MESSAGE` | `Please find below the L2 Project Dashboard...` | Copy from `.env` |
   | `EMAIL_FOOTER` | `This report is automatically generated...` | Copy from `.env` |
   | `EMAIL_SIGNATURE` | `Thanks & Regards,\nLalith Vishnu. S` | Copy from `.env` |
   | `GITHUB_TOKEN` | `github_pat_11B...` | Create new Personal Access Token |

   **How to add secrets:**
   - Click: **New repository secret**
   - Name: (e.g., `EMAIL_FROM`)
   - Value: (paste value from `.env`)
   - Click: **Add secret**
   - Repeat for all secrets above

3. **GitHub Actions Workflow file** (already exists):
   - Location: `.github/workflows/l2-report-daily.yml`
   - Runs on: Daily schedule (GitHub Cron format)
   - Triggers: `send_l2_report_smtp.py` (cloud email)

### Step 7️⃣: Create GitHub Personal Access Token

**If you don't have GITHUB_TOKEN yet:**

1. Go to: `https://github.com/settings/tokens`
2. Click: **Generate new token** → **Generate new token (classic)**
3. Configure:
   - Token name: `L2-Report-Action`
   - Expiration: `90 days` (rotate quarterly)
   - Scopes: Check ✅ `repo` (full control of private repositories)
4. Click: **Generate token**
5. **Copy the token immediately** (won't show again)
6. Add to GitHub Secrets as `GITHUB_TOKEN`

### Step 8️⃣: Verify GitHub Actions

1. Go to: `https://github.com/LalithVishnu-hub/L2-Report/actions`
2. Look for: `l2-report-daily` workflow
3. Check: **Scheduled runs** show upcoming dates
4. If red ❌: Click run → **View job logs** to debug

### Step 9️⃣: Test Cloud Execution

```powershell
# Trigger workflow manually (GitHub website)
1. Go to: Actions → l2-report-daily
2. Click: "Run workflow" → "Run workflow"
3. Wait 2-3 minutes
4. Check: Workflow Runs shows green ✅
5. Check: Email received from GitHub Actions
```

---

## 🔄 How L1 Reports Sync When Team Updates

### Scenario: Team updates Excel files in Box daily

**How sync happens:**

```
DAY 1 (4:00 PM):
  1. Script reads Excel files from: C:\Users\LalithVishnu\Box\L1 Report Repository
  2. Generates fresh L2_Report.html (with latest data)
  3. Generates fresh L1 pages: html_reports/L1/PID_XXXXX.html
  4. Sends email to recipients
  5. Git commits and pushes HTML to GitHub
  6. GitHub Pages deploys → Pages live at GitHub URLs

DAY 2 (4:00 PM):
  1. Excel files in Box folder have NEW data from team
  2. Script reads LATEST files (not cached, fresh read)
  3. Generates NEW L2_Report.html with updated data
  4. Generates NEW L1 pages with updated data
  5. Sends email with new data
  6. Git commit overwrites old HTML with new HTML
  7. GitHub Pages updates automatically
  8. Links in yesterday's email STILL WORK (same URLs, new content)
```

**Key points:**
- ✅ **No manual sync needed** - Script reads fresh files each run
- ✅ **Automatic updates** - GitHub Pages updates when files are committed
- ✅ **Persistent URLs** - Links don't change (same PID_XXXXX.html)
- ✅ **Backward compatible** - Old email links still work, show latest data
- ✅ **Real-time** - Every day gets latest data automatically

### What team does (NO code required):
1. Update Excel files in Box folder
2. Save and close Excel
3. That's it! Script will automatically read updated files next run

### What happens automatically:
1. Scheduled job reads latest files
2. Generates fresh reports
3. Sends new email
4. Updates GitHub Pages
5. Everyone sees latest data

**IMPORTANT:** Team does NOT need to:
- ❌ Run any scripts
- ❌ Commit code
- ❌ Push to GitHub
- ❌ Update anything else

Just update Excel files and save them!

---

## 📅 Configuration Examples

### Example 1: Change Schedule Time

**Requirement:** Run report at 6:00 PM instead of 4:00 PM

**Local (Task Scheduler):**
```env
# Edit .env
SCHEDULER_HOUR=18
SCHEDULER_MINUTE=0

# Re-apply schedule
powershell -ExecutionPolicy Bypass -File "L2_Report_Mail\fix_task_scheduler.ps1"
```

**Cloud (GitHub Actions):**
```yaml
# Edit .github/workflows/l2-report-daily.yml
schedule:
  - cron: '0 18 * * *'  # 18:00 UTC (or adjust for timezone)
```

### Example 2: Change Email Recipients

**Edit `.env`:**
```env
EMAIL_TO=person1@company.com, person2@company.com, person3@company.com
```

**For Cloud, also update GitHub Secrets:**
```
Go to: GitHub Settings → Secrets → EMAIL_TO
Update value to same as .env
```

### Example 3: Change Email Signature with Line Breaks

**Edit `.env`:**
```env
EMAIL_SIGNATURE=Thanks & Regards,\nLalith Vishnu\nTest Lead - ETE Project
```

**Result in email:**
```
Thanks & Regards,
Lalith Vishnu
Test Lead - ETE Project
```

---

## 🚀 WHEN TO USE LOCAL vs CLOUD

### Use LOCAL Task Scheduler If:
- ✅ Your PC runs 24/7
- ✅ You need reports during business hours only
- ✅ Outlook is available on your machine
- ✅ No internet interruptions needed
- ✅ Faster feedback (runs immediately on your PC)

### Use GITHUB ACTIONS (Cloud) If: ⭐ YOUR CASE
- ✅ PC can be OFF/asleep at scheduled time
- ✅ You need 24/7 consistent scheduling
- ✅ Traveling or remote working
- ✅ Team in different timezones
- ✅ No dependency on local infrastructure
- ✅ **YOUR REQUIREMENT: "trigger mail even when PC is shutdown"** ⭐

### Use BOTH If:
- ✅ You want redundancy/backup
- ✅ If local fails, cloud still sends
- ✅ If cloud fails, local still sends
- ✅ Maximum reliability

**FOR YOUR CASE: Use GitHub Actions (Cloud) - it meets your requirement!**

---

## 📋 Configuration Checklist

### Local Setup Checklist:
- [ ] Edited `.env` with your email details
- [ ] Set `SCHEDULER_HOUR` and `SCHEDULER_MINUTE`
- [ ] Ran `fix_task_scheduler.ps1`
- [ ] Verified task created: `Get-ScheduledTask -TaskName "L2_Report_Daily_ETE"`
- [ ] Tested: `python send_l2_report_outlook_account.py` sent email
- [ ] Task runs at correct time (monitored for 1 day)

### Cloud Setup Checklist: ⭐ RECOMMENDED
- [ ] Created GitHub Personal Access Token
- [ ] Added token to GitHub Secrets as `GITHUB_TOKEN`
- [ ] Added all `EMAIL_*` variables to GitHub Secrets
- [ ] Verified workflow file exists: `.github/workflows/l2-report-daily.yml`
- [ ] Tested: Manual workflow run succeeded
- [ ] Email received from GitHub Actions
- [ ] GitHub Pages updated automatically

### Team Sync Checklist:
- [ ] Team knows to update Excel files in Box folder
- [ ] Team saves Excel files (no special format needed)
- [ ] Your script reads latest files automatically
- [ ] GitHub Pages updates automatically (no manual deploy)
- [ ] Email links work with latest data

---

## 🔐 Security Best Practices

### `.env` File (Local):
```
✅ Keep LOCALLY ONLY
✅ In .gitignore (never committed)
✅ Contains sensitive data (tokens, credentials)
✅ Only your PC has it
```

### GitHub Secrets (Cloud):
```
✅ Stored encrypted on GitHub
✅ Never exposed in logs/output
✅ Each workflow has own secret copy
✅ Rotate Personal Access Token every 90 days
```

### GITHUB_TOKEN:
```
⚠️ CRITICAL: Never commit to git
⚠️ If accidentally leaked, regenerate immediately
✅ GitHub Push Protection prevents accidental commit
```

---

## 🆘 Troubleshooting

### Local (Task Scheduler) Troubleshooting:

**Problem:** Email not sending at scheduled time
```powershell
# Check if task exists
Get-ScheduledTask -TaskName "L2_Report_Daily_ETE"

# Check last run time and result
Get-ScheduledTaskInfo -TaskName "L2_Report_Daily_ETE"

# View task history
Get-WinEvent -LogPath "Microsoft-Windows-TaskScheduler/Operational" -MaxEvents 10
```

**Problem:** Task shows error
```powershell
# Check logs
Get-Content "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\logs\email_delivery_*.log"

# Re-run setup
powershell -ExecutionPolicy Bypass -File "L2_Report_Mail\fix_task_scheduler.ps1"
```

### Cloud (GitHub Actions) Troubleshooting:

**Problem:** Workflow not running
1. Go to: `https://github.com/LalithVishnu-hub/L2-Report/actions`
2. Click: `l2-report-daily`
3. Check: "Scheduled runs" shows upcoming dates
4. If no upcoming runs: Workflow may be disabled or schedule not set

**Problem:** Workflow fails
1. Click failed run
2. Click job name
3. Read error output
4. Common causes:
   - Missing secrets (check GitHub Secrets page)
   - Excel file format changed
   - Network connectivity issue

---

## ✨ Summary: Your Recommended Setup

**For your requirement: "Trigger mail even when PC is shutdown"**

### ⭐ Recommended: Use GitHub Actions (Cloud)

```
✅ Runs on schedule even if your PC is OFF
✅ No dependency on Task Scheduler
✅ Consistent 24/7 reporting
✅ Team emails guaranteed delivery
✅ GitHub Pages auto-updates
✅ Team just updates Excel - no other changes needed
```

### Setup Steps (Quick):
1. Edit `.env` with email details
2. Create GitHub Personal Access Token
3. Add secrets to GitHub (copy from `.env`)
4. Verify workflow file exists
5. Test with manual run
6. Team continues updating Excel files (no changes needed)

### Result:
```
Every day at scheduled time:
→ Email sent to team (regardless of your PC)
→ L1 reports updated on GitHub Pages
→ Team clicks links → sees latest data
→ No manual intervention needed
→ Works even when your PC is OFF ✅
```

**This is the most reliable setup for your requirement!** 🎯

---

## 📞 Support & Updates

### Configuration Files Location:
```
C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\
├── .env (LOCAL - edit this)
├── .github/workflows/l2-report-daily.yml (CLOUD config)
├── L2_Report_Mail/fix_task_scheduler.ps1 (LOCAL setup)
├── L2_Report_Mail/generate_L2_report.py (Main script)
└── CONFIGURATION.md (This file - keep it updated!)
```

### To Update Configuration:
1. Change `.env` file (local)
2. Re-run `fix_task_scheduler.ps1` if schedule changed
3. Update GitHub Secrets if using cloud
4. Test with manual run: `python send_l2_report_outlook_account.py`
5. Document changes in this file

---

Last Updated: 2026-06-25
