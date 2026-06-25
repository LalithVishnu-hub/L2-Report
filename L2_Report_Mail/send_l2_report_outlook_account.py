"""
L2 Report Email Sender via Outlook MAPI with Account Selection
Works with Outlook's existing account and delegates to Outlook for sending
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import logging

# Set up paths - both files in same folder now
parent_dir = Path(__file__).parent.parent
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Load environment variables
load_dotenv(str(parent_dir / '.env'), override=True)

# Setup logs directory and file (in parent directory)
logs_dir = parent_dir / 'logs'
logs_dir.mkdir(exist_ok=True)
log_file = logs_dir / f'email_delivery_{datetime.now().strftime("%Y%m%d")}.log'

# Configure logging - log to both file and console
# Using UTF-8 encoding to support special characters
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get Email Configuration from .env
EMAIL_FROM = os.getenv('EMAIL_FROM', 'lalvishn@in.ibm.com')
EMAIL_TO = os.getenv('EMAIL_TO', 'lalvishn@in.ibm.com,lv1087@att.com')
EMAIL_SUBJECT = os.getenv('EMAIL_SUBJECT') or os.getenv('EMAIL_SUBMIT') or 'L2 Project Dashboard Report - ETE Status Update'


def generate_l2_report():
    """Generate fresh L2 Report HTML"""
    logger.info("Generating L2 Report...")
    try:
        import generate_L2_report
        try:
            generate_L2_report.main()
        except:
            pass
        
        html_file = parent_dir / 'html_reports' / 'L2_Report.html'
        if html_file.exists():
            logger.info(f"[OK] L2_Report.html generated successfully")
            return True
        else:
            logger.error("L2_Report.html not found in html_reports folder")
            return False
    except Exception as e:
        logger.error(f"Error generating L2 Report: {e}")
        return False


def send_via_outlook_account():
    """Send email via Outlook with automatic account selection"""
    logger.info("=" * 80)
    logger.info("Using: Outlook Application with Account Delegation")
    logger.info("=" * 80)
    
    try:
        # Try to import win32com
        try:
            import win32com.client
        except ImportError:
            logger.warning("Installing pywin32...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pywin32"])
            import win32com.client
        
        logger.info("Connecting to Outlook...")
        
        # Get Outlook instance with retry logic for Task Scheduler compatibility
        outlook = None
        retry_count = 0
        max_retries = 3
        
        while not outlook and retry_count < max_retries:
            try:
                # Try to get existing Outlook instance first
                outlook = win32com.client.GetObject(None, "Outlook.Application")
                logger.info("[OK] Connected to existing Outlook instance")
                break
            except:
                retry_count += 1
                if retry_count < max_retries:
                    logger.info(f"Attempt {retry_count}: Starting Outlook application...")
                    try:
                        outlook = win32com.client.Dispatch("Outlook.Application")
                        logger.info("[OK] Outlook application started")
                        time.sleep(4)  # Wait for Outlook to fully initialize
                        break
                    except Exception as e:
                        logger.warning(f"  Retry {retry_count} failed: {e}")
                        if retry_count < max_retries:
                            time.sleep(2)
        
        if not outlook:
            logger.error("Could not connect to or start Outlook after multiple attempts")
            return False
        
        # Get Outlook namespace
        namespace = outlook.GetNamespace("MAPI")
        
        # Get the default account (user's primary email account)
        logger.info(f"Getting Outlook account for {EMAIL_FROM}...")
        
        html_file = parent_dir / 'html_reports' / 'L2_Report.html'
        if not html_file.exists():
            logger.error("L2_Report.html not found in html_reports folder")
            return False
            
        with open(html_file, 'r', encoding='utf-8') as f:
            email_body = f.read()
        
        logger.info(f"[OK] Email body loaded ({len(email_body)} bytes) from {html_file}")
        
        # Create mail item in Drafts folder for composing
        drafts_folder = namespace.GetDefaultFolder(3)  # 3 = olFolderDrafts
        mail_item = drafts_folder.Items.Add(0)  # 0 = olMailItem
        
        # Set email properties
        # Add recipients one by one using Outlook's Recipient object
        recipients = mail_item.Recipients
        for email_addr in EMAIL_TO.split(','):
            email_addr = email_addr.strip()
            if email_addr:
                try:
                    recipient = recipients.Add(email_addr)
                    recipient.Type = 1  # 1 = olTo
                    logger.info(f"  Added recipient: {email_addr}")
                except Exception as e:
                    logger.warning(f"  Failed to add {email_addr}: {e}")
        
        # Resolve all recipients
        try:
            recipients.ResolveAll()
            logger.info("  [OK] All recipients resolved")
        except Exception as e:
            logger.warning(f"  Warning resolving recipients: {e}")
        
        mail_item.Subject = EMAIL_SUBJECT
        mail_item.HTMLBody = email_body
        
        # Try to set the sending account if available
        try:
            # Set SendUsingAccount to the first available account
            accounts = outlook.Session.Accounts
            if accounts.Count > 0:
                for account in accounts:
                    if EMAIL_FROM.lower() in account.DisplayName.lower() or EMAIL_FROM.lower() in account.SmtpAddress.lower():
                        mail_item.SendUsingAccount = account
                        logger.info(f"  Using account: {account.DisplayName} ({account.SmtpAddress})")
                        break
                else:
                    # If exact match not found, use first account
                    mail_item.SendUsingAccount = accounts.Item(1)
                    logger.info(f"  Using account: {accounts.Item(1).DisplayName}")
        except:
            logger.info("  Using default account")
        
        logger.info(f"  To: {EMAIL_TO}")
        logger.info(f"  Subject: {EMAIL_SUBJECT}")
        logger.info(f"  Body: HTML ({len(email_body)} bytes)")
        
        # Send email
        logger.info("Sending email via Outlook...")
        mail_item.Send()
        
        logger.info("=" * 80)
        logger.info("[OK] EMAIL SENT SUCCESSFULLY VIA OUTLOOK!")
        logger.info(f"[OK] Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        return True
        
    except Exception as e:
        logger.error(f"❌ Outlook send failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def send_l2_report_email():
    """Send L2 Report via Outlook"""
    logger.info("=" * 80)
    logger.info(f"MANUAL EMAIL TRIGGER at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    try:
        # Generate report
        report_generated = generate_l2_report()
        if not report_generated:
            logger.error("Failed to generate L2 Report. Email not sent.")
            return False
        
        # Send via Outlook
        return send_via_outlook_account()
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("L2 REPORT EMAIL SENDER - OUTLOOK ACCOUNT (NO SMTP CREDENTIALS NEEDED)")
    print("=" * 80 + "\n")
    
    success = send_l2_report_email()
    
    if success:
        print("\n" + "=" * 80)
        print("SUCCESS: Email sent successfully!")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("FAILED: Email could not be sent")
        print("=" * 80)
        sys.exit(1)
