# GitHub Actions L2 Dashboard Automation Setup

This guide explains how to set up GitHub Actions to automatically send the L2 Dashboard report via email instead of using Windows Task Scheduler.

## Overview

The automation will:
- ✓ Run daily at **4:00 PM IST** (10:30 AM UTC)
- ✓ Generate the L2 Report from your data
- ✓ Send report via **IBM SMTP** email
- ✓ Backup database to GitHub Releases
- ✓ Keep the latest 30 days of reports as artifacts

## Setup Instructions

### Step 1: Add GitHub Secrets

GitHub Secrets are encrypted environment variables that GitHub Actions can use.

1. Go to your repository: https://github.com/LalithVishnu-hub/L2-Report
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** and add each of these secrets:

#### Required Secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `EMAIL_FROM` | Your IBM email address | `lalvishn@in.ibm.com` |
| `EMAIL_TO` | Recipients (comma-separated) | `lalvishn@in.ibm.com,lv1087@att.com` |
| `EMAIL_SUBJECT` | Email subject line | `L2 Project Dashboard Report - ETE Status Update` |
| `SMTP_SERVER` | IBM SMTP server | `smtp.ibm.com` |
| `SMTP_PORT` | SMTP port | `25` |
| `SMTP_USER` | Your IBM email or username | `lalvishn@in.ibm.com` or `lv1087` |
| `SMTP_PASS` | Your email password/app password | (your password) |
| `GITHUB_OWNER` | Your GitHub username | `LalithVishnu-hub` |
| `GITHUB_REPO` | Repository name | `L2-Report` |

**Note:** Leave `SMTP_PORT` and `SMTP_USER`/`SMTP_PASS` as they are if your IBM network uses:
- Port 25 (standard)
- No authentication

### Step 2: Upload Initial Database to GitHub Releases

1. Locate your current `L2_Report.db` file
2. Create a Release in your GitHub repository:
   - Go to **Releases** → **Create a new release**
   - Tag: `db-backup-initial`
   - Title: `Database Backup - Initial`
   - Upload file: `L2_Report.db`
   - Publish release

### Step 3: Update .env File (Optional Local Development)

Your `.env` file can stay as-is. When running locally, it will use the Outlook method. When running in GitHub Actions, it will use the SMTP method based on environment variables.

```env
# For local Outlook (Windows only)
EMAIL_FROM=lalvishn@in.ibm.com
EMAIL_TO=lv1087@att.com
EMAIL_SUBJECT=L2 Project Dashboard Report - ETE Status Update
SMTP_SERVER=smtp.ibm.com
SMTP_PORT=25
SMTP_USER=
SMTP_PASS=
```

### Step 4: Test the Workflow

1. Go to your repository's **Actions** tab
2. Select **"Send L2 Dashboard Report"** workflow
3. Click **"Run workflow"** → **"Run workflow"**
4. Monitor the execution in real-time
5. Check the run logs for any errors

## Scheduled Execution

The workflow runs automatically:
- **Schedule:** Daily at 4:00 PM IST (10:30 AM UTC)
- **Cron expression:** `30 10 * * *` (in `.github/workflows/send-l2-report.yml`)

To change the schedule, edit the cron expression:
- 4:00 PM UTC: `0 16 * * *`
- 5:00 PM UTC: `0 17 * * *`
- Or use an online cron generator: https://crontab.guru/

## Database Management

### Automatic Backup
Every workflow run creates a new release with the database backup (if database changed).

### Manual Download
```bash
# Download latest database
python scripts/download_database_from_releases.py

# Upload database
python scripts/upload_database_to_releases.py
```

## Troubleshooting

### Email Not Sending

**Error: SMTP Authentication failed**
- Check your IBM email/password in GitHub Secrets
- Verify SMTP_SERVER and SMTP_PORT are correct
- Some corporate networks require VPN to access SMTP

**Error: Connection timeout**
- Check network connectivity (GitHub Actions runs on Azure servers)
- Some corporate firewalls block SMTP port 25
- Try port 587 with TLS enabled

### Workflow Not Running

**Check:**
1. Workflow file exists: `.github/workflows/send-l2-report.yml`
2. Workflow is enabled (check Actions tab)
3. Repository is public or GitHub Actions is enabled for private repos

### Database Not Found

**Solution:**
- Manually upload initial database to Releases (see Step 2)
- Or disable database backup in workflow temporarily

## Files Added/Modified

### New Files:
- `.github/workflows/send-l2-report.yml` - Main workflow configuration
- `L2_Report_Mail/send_l2_report_smtp.py` - SMTP email sender (works in GitHub Actions)
- `scripts/download_database_from_releases.py` - Download DB from releases
- `scripts/upload_database_to_releases.py` - Backup DB to releases

### Existing Files:
- `L2_Report_Mail/generate_L2_report.py` - No changes needed (still works)

## Disabling Automation

To disable the scheduled automation:

**Option 1:** Disable the workflow
- Go to **Actions** → **Send L2 Dashboard Report**
- Click **...** → **Disable workflow**

**Option 2:** Delete the workflow file
- Delete `.github/workflows/send-l2-report.yml`
- Commit and push to main

You can still run it manually by clicking **"Run workflow"** in the Actions tab.

## Alternative Email Methods

### Gmail (if needed)
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-specific-password
```

### Outlook.com / Office 365
```
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASS=your-password
```

## Security Best Practices

✓ **Do:**
- Store passwords in GitHub Secrets (encrypted)
- Use app-specific passwords instead of main password
- Review workflow logs for errors
- Keep repository private if handling sensitive data

✗ **Don't:**
- Commit `.env` with passwords to Git
- Share GitHub token publicly
- Use plain-text passwords in workflow file

## Support

If automation fails:
1. Check the **Actions** tab for error logs
2. Verify all GitHub Secrets are set correctly
3. Test email credentials locally
4. Check IBM network connectivity / VPN requirements
