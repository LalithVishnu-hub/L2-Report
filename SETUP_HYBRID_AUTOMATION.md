# ✅ Simplified GitHub Actions Setup (Local + Cloud Hybrid)

## Architecture

Your setup is **HYBRID** - your local PC does the heavy lifting, GitHub does the email:

```
Your Local PC (Windows)
  ↓
  ├─ Task Scheduler: Pulls L2 data from Box folder  
  ├─ generate_L2_report.py: Creates HTML report
  ├─ Git push: Uploads report to GitHub
  ↓
GitHub Actions Cloud
  ↓
  └─ Detects report change → Automatically sends email ✉️
```

## What You Need to Do

### Step 1: Add GitHub Secrets (5 min) ⚡
Go to: https://github.com/LalithVishnu-hub/L2-Report/settings/secrets/actions

Add ONLY these 4 email secrets:
| Secret | Value |
|--------|-------|
| `EMAIL_FROM` | `lalvishn@in.ibm.com` |
| `EMAIL_TO` | `lv1087@att.com` |
| `EMAIL_SUBJECT` | `L2 Project Dashboard Report - ETE Status Update` |
| `SMTP_SERVER` | `smtp.ibm.com` |
| `SMTP_PORT` | `25` |

Leave `SMTP_USER` and `SMTP_PASS` empty (IBM doesn't require auth on port 25).

### Step 2: Keep Your Local Task Scheduler ✅
**Don't change anything!** Your current setup is perfect:
- ✅ Task Scheduler runs daily at 4 PM
- ✅ Pulls data from `C:\Users\LalithVishnu\Box\L1 Report Repository`
- ✅ Generates `html_reports/L2_Report.html`
- ✅ Pushes changes to GitHub

### Step 3: Workflow Automation 🚀
**After Step 2, GitHub Actions takes over automatically:**

1. Your Task Scheduler generates the report
2. You commit and push to GitHub (`git push`)
3. GitHub Actions **detects the change**
4. GitHub Actions **automatically sends the email**

## How It Works

### Flow Each Day:

**4:00 PM IST (Local PC)**
```
Task Scheduler triggers
  ↓
generate_L2_report.py runs
  ↓
Data pulled from Box folder
  ↓
HTML report created
  ↓
(Auto-commit if using auto-push script)
  ↓
Git push to GitHub
```

**Immediately After (GitHub Cloud)**
```
GitHub detects html_reports/L2_Report.html changed
  ↓
GitHub Actions workflow triggers automatically
  ↓
send_l2_report_smtp.py runs
  ↓
Email sent to lv1087@att.com ✓
  ↓
Report saved as artifact (30 days)
```

## What Changed from Previous Setup

| Old Setup | New Setup |
|-----------|-----------|
| Local Task Scheduler sends email via Outlook | Local Task Scheduler only generates report |
| No GitHub integration for email | GitHub Actions sends email automatically |
| Had to have local PC running 24/7 for scheduler | Only need PC running at 4 PM IST |
| No email history/logs | All runs logged in Actions tab |

## No More Files Needed!

You do **NOT** need to:
- ❌ Upload database to releases
- ❌ Set GITHUB_OWNER / GITHUB_REPO secrets
- ❌ Use `scripts/download_database_from_releases.py`
- ❌ Use `scripts/upload_database_to_releases.py`

These files can be **deleted** from the repo.

## Testing

### Manual Trigger (to test email)
1. Go to: https://github.com/LalithVishnu-hub/L2-Report/actions
2. Select **"Send L2 Dashboard Report"**
3. Click **"Run workflow"**
4. Check email in 1-2 minutes

### Automatic Trigger (after local script)
1. Your Task Scheduler generates report
2. Push to GitHub: `git push`
3. GitHub Actions runs automatically (no manual action needed)
4. Email arrives within 2-3 minutes

## Troubleshooting

### No email received after push?
1. Check: https://github.com/LalithVishnu-hub/L2-Report/actions
2. Look for failed runs (red ✗)
3. Click run → View logs for errors
4. Most common: SMTP secrets not set correctly

### Workflow didn't trigger after push?
- Workflow only triggers when `html_reports/L2_Report.html` file changes
- If you're not updating that file, no trigger occurs
- Solution: Manually run via "Run workflow" button

### Got email about "Run failed"?
- This means workflow tried to send but failed
- Check GitHub Secrets are correct
- Verify report file exists in repository

## Security

✅ **Good Practices:**
- Email credentials stored encrypted in GitHub Secrets
- Never committed to repository
- Only accessible to Actions workflows

⚠️ **Note:** Anyone with push access to repo can view workflow runs and artifacts.

## Disabling Email Automation

To stop automated emails:
1. Delete the workflow file: `.github/workflows/send-l2-report.yml`
2. Or disable in Actions tab
3. Local Task Scheduler continues working (emails just won't be sent via GitHub)

## Summary

**You:** Generate report locally (unchanged) + push to GitHub  
**GitHub:** Automatically sends email when report changes  
**Result:** Fully automated, no manual email sending needed! 🎉
