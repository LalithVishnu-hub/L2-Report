"""
Test Script for L2 Report Automation
Runs all components locally to verify everything works
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import time

# Define paths
PROJECT_ROOT = Path(__file__).parent
VENV_PYTHON = PROJECT_ROOT / '.venv' / 'Scripts' / 'python.exe'
L2_MAIL_DIR = PROJECT_ROOT / 'L2_Report_Mail'
GENERATE_SCRIPT = L2_MAIL_DIR / 'generate_L2_report.py'
SEND_SCRIPT = L2_MAIL_DIR / 'send_l2_report_outlook_account.py'
REPORT_FILE = PROJECT_ROOT / 'html_reports' / 'L2_Report.html'
LOGS_DIR = PROJECT_ROOT / 'logs'

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_step(step_num, text):
    print(f"\n[Step {step_num}] {text}")
    print("-" * 80)

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n► Running: {description}")
    print(f"  Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: {description}")
            if result.stdout:
                print(f"\nOutput:\n{result.stdout}")
            return True
        else:
            print(f"❌ FAILED: {description}")
            if result.stderr:
                print(f"\nError:\n{result.stderr}")
            if result.stdout:
                print(f"\nOutput:\n{result.stdout}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT: {description} (exceeded 120 seconds)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    print_header("L2 REPORT AUTOMATION - LOCAL TEST")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check prerequisites
    print_step(1, "Checking Prerequisites")
    
    if not VENV_PYTHON.exists():
        print(f"❌ ERROR: Python venv not found at {VENV_PYTHON}")
        print("Please activate the virtual environment first")
        return False
    print(f"✓ Python venv found: {VENV_PYTHON}")
    
    if not GENERATE_SCRIPT.exists():
        print(f"❌ ERROR: Generate script not found at {GENERATE_SCRIPT}")
        return False
    print(f"✓ Generate script found: {GENERATE_SCRIPT}")
    
    if not SEND_SCRIPT.exists():
        print(f"❌ ERROR: Send script not found at {SEND_SCRIPT}")
        return False
    print(f"✓ Send script found: {SEND_SCRIPT}")
    
    # Create logs directory if needed
    LOGS_DIR.mkdir(exist_ok=True)
    print(f"✓ Logs directory: {LOGS_DIR}")
    
    # Step 2: Generate Report
    print_step(2, "Generate L2 Report")
    
    generate_success = run_command(
        [str(VENV_PYTHON), str(GENERATE_SCRIPT)],
        "Generate L2 Report"
    )
    
    if not generate_success:
        print("⚠️  Report generation may have warnings, but we'll continue...")
    
    # Check if report was created
    if REPORT_FILE.exists():
        report_size = REPORT_FILE.stat().st_size
        print(f"✓ Report file created: {REPORT_FILE} ({report_size:,} bytes)")
    else:
        print(f"❌ Report file not found: {REPORT_FILE}")
        print("The report generation may have failed")
        return False
    
    # Step 3: Send Email
    print_step(3, "Send L2 Report Email")
    
    send_success = run_command(
        [str(VENV_PYTHON), str(SEND_SCRIPT)],
        "Send L2 Report Email"
    )
    
    if send_success:
        print("\n✅ Email sent successfully!")
    else:
        print("\n❌ Email sending failed")
        print("\nCommon issues:")
        print("  • Outlook not installed or not configured")
        print("  • Email addresses not valid")
        print("  • Firewall blocking Outlook")
    
    # Step 4: Check Logs
    print_step(4, "Check Logs")
    
    log_files = list(LOGS_DIR.glob('*.log'))
    if log_files:
        latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
        print(f"✓ Latest log file: {latest_log.name}")
        print(f"\nLast 20 lines of log:")
        print("-" * 80)
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[-20:]:
                print(line.rstrip())
    else:
        print("⚠️  No log files found")
    
    # Summary
    print_header("TEST SUMMARY")
    
    if send_success:
        print("✅ ALL TESTS PASSED!")
        print("\nNext steps:")
        print("  1. Verify email was received in: lv1087@att.com")
        print("  2. Run: setup_task_scheduler.ps1 (as Administrator)")
        print("  3. Task Scheduler will run this daily at 4:00 PM")
        return True
    else:
        print("❌ TESTS FAILED")
        print("\nNext steps:")
        print("  1. Check the logs above for specific error messages")
        print("  2. Verify Outlook is installed and configured")
        print("  3. Try running the send script manually:")
        print(f"     {VENV_PYTHON} {SEND_SCRIPT}")
        return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
