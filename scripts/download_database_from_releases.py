"""
Download L2 Report database from GitHub Releases
"""

import os
import sys
import requests
import json
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get credentials from environment
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITHUB_OWNER = os.getenv('GITHUB_OWNER', 'LalithVishnu-hub')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'L2-Report')

# Database file location
DB_FILE = Path(__file__).parent.parent / 'L2_Report.db'

GITHUB_API = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}" if GITHUB_TOKEN else ""
}


def download_database():
    """Download the latest database from GitHub Releases"""
    logger.info("Downloading L2 Report database from GitHub Releases...")
    
    try:
        # Get latest release
        url = f"{GITHUB_API}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
        logger.info(f"Fetching: {url}")
        
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        release_data = response.json()
        logger.info(f"Latest release: {release_data.get('tag_name', 'unknown')}")
        
        # Find database asset
        assets = release_data.get('assets', [])
        db_asset = None
        
        for asset in assets:
            if asset['name'].endswith('.db') or asset['name'] == 'L2_Report.db':
                db_asset = asset
                break
        
        if not db_asset:
            logger.warning("No database file found in latest release")
            logger.info("Will use existing database or create new one")
            return True
        
        logger.info(f"Found database: {db_asset['name']} ({db_asset['size'] / 1024:.2f} KB)")
        
        # Download asset
        download_url = db_asset['browser_download_url']
        logger.info(f"Downloading from: {download_url}")
        
        response = requests.get(download_url, headers=HEADERS, timeout=60)
        response.raise_for_status()
        
        # Save database
        with open(DB_FILE, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"✓ Database saved: {DB_FILE} ({DB_FILE.stat().st_size / 1024:.2f} KB)")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ Failed to download database: {e}")
        logger.info("Will use existing database or create new one")
        return True  # Don't fail the workflow
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}")
        return True  # Don't fail the workflow


if __name__ == '__main__':
    success = download_database()
    sys.exit(0 if success else 1)
