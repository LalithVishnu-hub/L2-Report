# ✅ GitHub Actions Setup Checklist

Complete these steps to enable automated L2 Dashboard email sending via GitHub Actions:

## Immediate Actions Required

### 1. Configure GitHub Secrets (5 min)
[ ] Go to: https://github.com/LalithVishnu-hub/L2-Report/settings/secrets/actions
[ ] Click "New repository secret" for each:
    [ ] `EMAIL_FROM` = `lalvishn@in.ibm.com`
    [ ] `EMAIL_TO` = `lalvishn@in.ibm.com,lv1087@att.com` (comma-separated)
    [ ] `EMAIL_SUBJECT` = `L2 Project Dashboard Report - ETE Status Update`
    [ ] `SMTP_SERVER` = `smtp.ibm.com`
    [ ] `SMTP_PORT` = `25`
    [ ] `SMTP_USER` = (leave empty for IBM network)
    [ ] `SMTP_PASS` = (leave empty for IBM network)
    [ ] `GITHUB_OWNER` = `LalithVishnu-hub`
    [ ] `GITHUB_REPO` = `L2-Report`

### 2. Upload Database Backup (3 min)
[ ] Go to: https://github.com/LalithVishnu-hub/L2-Report/releases
[ ] Click "Create a new release"
[ ] Fill in:
    - Tag: `db-backup-initial`
    - Title: `Database Backup - Initial`
    - Upload file: Select your `L2_Report.db`
[ ] Click "Publish release"

### 3. Test the Workflow (2 min)
[ ] Go to: https://github.com/LalithVishnu-hub/L2-Report/actions
[ ] Click "Send L2 Dashboard Report" workflow
[ ] Click "Run workflow" → "Run workflow"
[ ] Monitor execution (should complete in 2-3 minutes)
[ ] Check for any errors in the logs

### 4. Verify Automation
[ ] Check your email for test report
[ ] Confirm report generation and content looks correct

## Optional: IBM Network Setup

If behind IBM firewall and SMTP fails:
- [ ] Verify VPN is connected (if required)
- [ ] Try with `SMTP_USER` = your IBM email (with authentication)
- [ ] Contact IBM IT for SMTP configuration

## Next Steps

After setup:
- ✓ Automation runs daily at **4:00 PM IST**
- ✓ Reports auto-send to: `lv1087@att.com`
- ✓ Database backed up automatically
- ✓ Old Task Scheduler job can be deleted

## Disable Task Scheduler

Once GitHub Actions is working:
1. Open **Task Scheduler** (Windows)
2. Delete the old L2 Report scheduler task
3. No need to run local scripts manually

## Files Added

- `.github/workflows/send-l2-report.yml` - Automation workflow
- `L2_Report_Mail/send_l2_report_smtp.py` - SMTP email sender
- `scripts/download_database_from_releases.py` - DB sync
- `scripts/upload_database_to_releases.py` - DB backup
- `GITHUB_ACTIONS_SETUP.md` - Detailed setup guide

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Workflow fails to run | Check GitHub Secrets are set correctly |
| Email not sent | Verify SMTP_SERVER and credentials |
| Database not found | Upload initial backup to Releases (Step 2) |
| Port connection error | May require VPN or firewall exception |

## View Status

- Workflow runs: https://github.com/LalithVishnu-hub/L2-Report/actions
- Latest reports: https://github.com/LalithVishnu-hub/L2-Report/actions/artifacts
- Database backups: https://github.com/LalithVishnu-hub/L2-Report/releases

---

**Setup Time:** ~10 minutes | **Monthly Maintenance:** ~0 minutes
