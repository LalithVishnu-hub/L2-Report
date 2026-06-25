"""
L2 Report Email Sender via SMTP (works in GitHub Actions and local machines)
Supports IBM SMTP, Outlook, Gmail, and other SMTP servers
"""

import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Set up paths
parent_dir = Path(__file__).parent.parent
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Load environment variables
load_dotenv(str(parent_dir / '.env'), override=True)

# Setup logs directory
logs_dir = parent_dir / 'logs'
logs_dir.mkdir(exist_ok=True)
log_file = logs_dir / f'email_delivery_{datetime.now().strftime("%Y%m%d")}.log'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get Email Configuration from .env or GitHub Secrets
EMAIL_FROM = os.getenv('EMAIL_FROM', 'lalvishn@in.ibm.com')
EMAIL_TO = os.getenv('EMAIL_TO', 'lalvishn@in.ibm.com,lv1087@att.com')
EMAIL_SUBJECT = os.getenv('EMAIL_SUBJECT') or os.getenv('EMAIL_SUBMIT') or 'L2 Project Dashboard Report - ETE Status Update'

# SMTP Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.ibm.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '25'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASS = os.getenv('SMTP_PASS', '')
SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'false').lower() == 'true'
SMTP_USE_AUTH = os.getenv('SMTP_USE_AUTH', 'false').lower() == 'true'


def send_l2_report_email():
    """Send L2 Report via SMTP"""
    logger.info("=" * 60)
    logger.info("Starting L2 Report Email Delivery via SMTP")
    logger.info("=" * 60)
    
    try:
        # Get report file path
        report_path = parent_dir / 'html_reports' / 'L2_Report.html'
        
        if not report_path.exists():
            logger.error(f"Report file not found: {report_path}")
            return False
        
        logger.info(f"Report file found: {report_path}")
        logger.info(f"Report size: {report_path.stat().st_size / 1024:.2f} KB")
        
        # Read report content
        with open(report_path, 'r', encoding='utf-8') as f:
            report_html = f.read()
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = EMAIL_SUBJECT
        msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        logger.info(f"From: {EMAIL_FROM}")
        logger.info(f"To: {EMAIL_TO}")
        logger.info(f"Subject: {EMAIL_SUBJECT}")
        
        # Create plain text version
        text_version = "L2 Project Dashboard Report - Please see attached HTML report."
        part1 = MIMEText(text_version, 'plain')
        msg.attach(part1)
        
        # Create HTML version
        part2 = MIMEText(report_html, 'html')
        msg.attach(part2)
        
        # Attach HTML file
        attachment_filename = f'L2_Report_{datetime.now().strftime("%Y%m%d")}.html'
        with open(report_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {attachment_filename}')
            msg.attach(part)
        
        logger.info(f"Attachment: {attachment_filename}")
        
        # Connect and send
        logger.info(f"Connecting to SMTP server: {SMTP_SERVER}:{SMTP_PORT}")
        logger.info(f"TLS: {SMTP_USE_TLS}, Auth: {SMTP_USE_AUTH}")
        
        try:
            if SMTP_USE_TLS:
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
                server.starttls()
            else:
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
            
            if SMTP_USE_AUTH and SMTP_USER:
                logger.info(f"Authenticating as: {SMTP_USER}")
                server.login(SMTP_USER, SMTP_PASS)
            
            # Send email
            email_list = [e.strip() for e in EMAIL_TO.split(',')]
            logger.info(f"Sending to {len(email_list)} recipient(s)...")
            server.send_message(msg)
            
            logger.info("✓ Email sent successfully!")
            server.quit()
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"✗ SMTP Authentication failed: {e}")
            logger.error("Check SMTP_USER and SMTP_PASS in .env or GitHub Secrets")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"✗ SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Connection error: {e}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}")
        logger.error(traceback.format_exc())
        return False
    finally:
        logger.info("=" * 60)


if __name__ == '__main__':
    success = send_l2_report_email()
    sys.exit(0 if success else 1)
