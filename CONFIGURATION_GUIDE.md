# Configuration Guide - Single Place to Update Settings

## 📝 Where to Edit All Configuration

**Edit ONLY in ONE place:** `.env` file in the project root
- Location: `C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\.env`
- This file is automatically loaded by all Python scripts
- Changes take effect immediately when you run the scripts

---

## 🔧 Email Configuration Variables

Edit these in your `.env` file:

```env
# FROM address
EMAIL_FROM=lalvishn@in.ibm.com

# TO recipient
EMAIL_TO=your-email@example.com

# Subject line
EMAIL_SUBJECT=L2 Project Dashboard Report - ETE Status Update

# Opening greeting
EMAIL_GREETING=Hi All,

# Introduction message
EMAIL_INTRO_MESSAGE=Please find below the L2 Project Dashboard for ETE Wireline Projects.

# Footer text before signature
EMAIL_FOOTER=This report is automatically generated and sent daily. For any questions or clarifications regarding the projects listed above, please reach out to the respective Test Lead or Test Manager.

# Signature (use \n for line breaks)
EMAIL_SIGNATURE=Thanks & Regards,\nLalith Vishnu. S
```

---

## 💾 Local vs Cloud Execution

| What | Where to Update | How It Works |
|------|-----------------|--------------|
| **Local Testing** | Edit `.env` file | Run `python generate_L2_report.py` locally |
| **Scheduled Email (Cloud/GitHub Actions)** | GitHub Secrets + `.env` | Workflow reads GitHub Secrets environment variables |
| **Static Pages (GitHub Pages)** | Only `.env` (for testing) | Pages are generated from Excel files, no secrets needed |

---

## 🚀 Workflow: How to Change Email Details

### Option 1: For Local Testing Only
1. Edit `.env` file with your desired values
2. Run the script locally: `python L2_Report_Mail\generate_L2_report.py`
3. Email sends via Outlook using updated values

### Option 2: For Scheduled Cloud Execution (GitHub Actions)
1. Edit `.env` file locally (for reference)
2. Go to GitHub Repository → **Settings** → **Secrets and variables** → **Actions**
3. Update each secret to match your `.env` values:
   - `EMAIL_FROM`
   - `EMAIL_TO`
   - `EMAIL_SUBJECT`
   - `EMAIL_GREETING`
   - `EMAIL_INTRO_MESSAGE`
   - `EMAIL_FOOTER`
   - `EMAIL_SIGNATURE`
4. Commit the `.env` changes (it's in .gitignore, won't upload)
5. The workflow automatically reads GitHub Secrets on each scheduled run

---

## 📋 Configuration Checklist

- [ ] Updated `EMAIL_FROM` in `.env`
- [ ] Updated `EMAIL_TO` in `.env`
- [ ] Updated `EMAIL_SUBJECT` in `.env`
- [ ] Updated `EMAIL_GREETING` in `.env`
- [ ] Updated `EMAIL_INTRO_MESSAGE` in `.env`
- [ ] Updated `EMAIL_FOOTER` in `.env`
- [ ] Updated `EMAIL_SIGNATURE` in `.env` (use `\n` for line breaks)
- [ ] If using GitHub Actions: Updated same values in GitHub Secrets
- [ ] Tested locally by running `python L2_Report_Mail/generate_L2_report.py`

---

## 🔐 Security Note

- `.env` is in `.gitignore` - it never uploads to GitHub
- Sensitive data (tokens, passwords) belong only in GitHub Secrets
- Always edit `.env` locally for testing before updating GitHub Secrets

---

## 📱 Signature Line Break Example

To make your signature appear on multiple lines, use `\n`:

```env
EMAIL_SIGNATURE=Thanks & Regards,\nLalith Vishnu. S
```

This renders as:
```
Thanks & Regards,
Lalith Vishnu. S
```
