"""
One-time Box authentication setup.
Run this script ONCE to authorize the app and save tokens.

Steps:
    1. Set BOX_CLIENT_ID and BOX_CLIENT_SECRET in your .env file
       (get these from developer.box.com → Your App → Configuration)
    2. Run: python setup_box_auth.py
    3. Authorize in the browser that opens
    4. Done — daily reports will authenticate automatically from now on
"""

import sys
from pathlib import Path

# Add L2_Report_Mail to path
sys.path.insert(0, str(Path(__file__).parent / 'L2_Report_Mail'))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env', override=True)

from box_integration import setup_box_auth

if __name__ == '__main__':
    setup_box_auth()
