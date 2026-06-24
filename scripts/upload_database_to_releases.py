"""
Upload L2 Report database to GitHub Releases
"""

import os
import sys
import requests
import json
import subprocess
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


def create_release():
    """Create a new release for the database backup"""
    try:
        if not GITHUB_TOKEN:
            logger.warning("GITHUB_TOKEN not set, skipping database upload")
            return True
        
        if not DB_FILE.exists():
            logger.warning(f"Database file not found: {DB_FILE}")
            return True
        
        logger.info("Creating GitHub release for database backup...")
        
        # Create tag name with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        tag_name = f"db-backup-{timestamp}"
        release_name = f"Database Backup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Create release
        url = f"{GITHUB_API}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases"
        
        payload = {
            "tag_name": tag_name,
            "name": release_name,
            "body": "Automated database backup from GitHub Actions",
            "draft": False,
            "prerelease": False
        }
        
        response = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        
        if response.status_code != 201:
            logger.error(f"Failed to create release: {response.status_code} - {response.text}")
            return False
        
        release_data = response.json()
        upload_url = release_data['upload_url'].replace('{?name,label}', '')
        release_id = release_data['id']
        
        logger.info(f"✓ Release created: {tag_name}")
        logger.info(f"Uploading database file: {DB_FILE.name}")
        
        # Upload asset
        with open(DB_FILE, 'rb') as f:
            upload_headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Content-Type": "application/octet-stream"
            }
            
            upload_response = requests.post(
                f"{upload_url}?name={DB_FILE.name}",
                headers=upload_headers,
                data=f,
                timeout=60
            )
            
            if upload_response.status_code not in [200, 201]:
                logger.error(f"Failed to upload asset: {upload_response.status_code}")
                return False
        
        logger.info(f"✓ Database uploaded successfully")
        logger.info(f"Release: https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases/tag/{tag_name}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error uploading database: {e}")
        return False


if __name__ == '__main__':
    success = create_release()
    sys.exit(0 if success else 1)
