"""
Windows Task Scheduler Setup Script for L2 Report Automation
This script creates a scheduled task that sends L2 reports at 12:00 AM daily.
The report will still be sent even if the system is shut down.

Run with: python setup_task_scheduler.ps1 (PowerShell as Administrator)
OR:       python setup_task_scheduler.py (from Command Prompt as Administrator)
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# Get the paths
SCRIPT_DIR = Path(__file__).parent
PYTHON_EXE = sys.executable
SEND_REPORTS_SCRIPT = SCRIPT_DIR / 'send_reports.py'
VENV_DIR = SCRIPT_DIR / '.venv'

# Task configuration
TASK_NAME = 'L2_Report_Automation'
TASK_DESCRIPTION = 'Sends L2 Project Dashboard Report daily at 12:00 AM via email'
TASK_TIME = '00:00'  # 12:00 AM
TASK_REPEAT_INTERVAL = 'DAILY'  # Daily repetition


def setup_logging():
    """Setup logging."""
    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"task_setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return log_file


def check_admin_privileges():
    """Check if running with administrator privileges."""
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        return is_admin
    except Exception:
        return False


def create_task_via_powershell():
    """Create scheduled task using PowerShell."""
    
    logger.info("Creating scheduled task via PowerShell...")
    
    # Determine which Python executable to use
    if VENV_DIR.exists():
        python_exe = VENV_DIR / 'Scripts' / 'python.exe'
    else:
        python_exe = PYTHON_EXE
    
    python_exe_str = str(python_exe).replace('\\', '\\\\')
    send_reports_str = str(SEND_REPORTS_SCRIPT).replace('\\', '\\\\')
    
    # PowerShell script to create task
    ps_script = f"""
    $taskName = '{TASK_NAME}'
    $taskDescription = '{TASK_DESCRIPTION}'
    $taskTime = '{TASK_TIME}'
    $pythonExe = '{python_exe_str}'
    $sendReportsScript = '{send_reports_str}'
    $workingDirectory = '{str(SCRIPT_DIR).replace(chr(92), chr(92)+chr(92))}'
    
    # Check if task already exists
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    
    if ($existingTask) {{
        Write-Output "Task '$taskName' already exists. Updating..."
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }}
    
    # Create action
    $action = New-ScheduledTaskAction `
        -Execute $pythonExe `
        -Argument "`"$sendReportsScript`" --mode send" `
        -WorkingDirectory $workingDirectory
    
    # Create trigger (daily at specified time)
    $trigger = New-ScheduledTaskTrigger `
        -Daily `
        -At $taskTime `
        -RandomDelay (New-TimeSpan -Minutes 5)
    
    # Create principal (run as system, which doesn't stop on shutdown)
    $principal = New-ScheduledTaskPrincipal `
        -UserId "SYSTEM" `
        -LogonType ServiceAccount `
        -RunLevel Highest
    
    # Create settings
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable `
        -MultipleInstances IgnoreNew `
        -ExecutionTimeLimit (New-TimeSpan -Hours 1)
    
    # Register the task
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Principal $principal `
        -Settings $settings `
        -Description $taskDescription `
        -Force
    
    Write-Output "Task '$taskName' created successfully!"
    Write-Output "Scheduled time: Daily at $taskTime"
    Write-Output "Next run time will be displayed when you check Task Scheduler"
    """
    
    try:
        # Run PowerShell script
        result = subprocess.run(
            ['powershell', '-NoProfile', '-Command', ps_script],
            capture_output=True,
            text=True,
            check=False
        )
        
        logger.info("PowerShell Output:")
        logger.info(result.stdout)
        
        if result.returncode == 0:
            logger.info("✓ Task created successfully via PowerShell!")
            return True
        else:
            logger.error("PowerShell Error:")
            logger.error(result.stderr)
            return False
            
    except Exception as e:
        logger.error(f"Error running PowerShell: {e}")
        return False


def create_task_via_schtasks():
    """Create scheduled task using schtasks.exe (fallback method)."""
    
    logger.info("Creating scheduled task via schtasks.exe...")
    
    # Determine which Python executable to use
    if VENV_DIR.exists():
        python_exe = VENV_DIR / 'Scripts' / 'python.exe'
    else:
        python_exe = PYTHON_EXE
    
    # Build command for schtasks
    cmd = [
        'schtasks',
        '/create',
        '/tn', TASK_NAME,
        '/tr', f'"{python_exe}" "{SEND_REPORTS_SCRIPT}" --mode send',
        '/sc', 'daily',
        '/st', TASK_TIME,
        '/f',  # Force creation, overwrite if exists
        '/rl', 'highest',  # Run with highest privileges
        '/ru', 'SYSTEM',  # Run as SYSTEM account (won't be interrupted by shutdown)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        logger.info("schtasks Output:")
        logger.info(result.stdout)
        
        if result.returncode == 0:
            logger.info("✓ Task created successfully via schtasks!")
            return True
        else:
            logger.error("schtasks Error:")
            logger.error(result.stderr)
            return False
            
    except Exception as e:
        logger.error(f"Error running schtasks: {e}")
        return False


def list_scheduled_task():
    """List the scheduled task details."""
    
    logger.info(f"Checking scheduled task: {TASK_NAME}")
    
    try:
        result = subprocess.run(
            ['schtasks', '/query', '/tn', TASK_NAME, '/v', '/fo', 'list'],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            logger.info("Task Details:")
            logger.info(result.stdout)
            return True
        else:
            logger.warning("Task not found or error querying task")
            return False
            
    except Exception as e:
        logger.error(f"Error listing task: {e}")
        return False


def delete_scheduled_task():
    """Delete the scheduled task."""
    
    logger.info(f"Deleting scheduled task: {TASK_NAME}")
    
    try:
        result = subprocess.run(
            ['schtasks', '/delete', '/tn', TASK_NAME, '/f'],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            logger.info("✓ Task deleted successfully")
            return True
        else:
            logger.warning("Error deleting task")
            logger.warning(result.stderr)
            return False
            
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return False


def main():
    """Main function."""
    
    log_file = setup_logging()
    logger.info("=" * 70)
    logger.info("L2 Report Automation - Task Scheduler Setup")
    logger.info("=" * 70)
    logger.info(f"Log file: {log_file}")
    logger.info("")
    
    # Check admin privileges
    if not check_admin_privileges():
        logger.error("✗ This script requires Administrator privileges!")
        logger.error("Please run as Administrator:")
        logger.error(f"  python {__file__}")
        logger.error("    OR")
        logger.error(f"  powershell -ExecutionPolicy Bypass -Command \"& python {__file__}\"")
        return False
    
    logger.info("✓ Running with Administrator privileges")
    logger.info("")
    
    # Validate paths
    if not SEND_REPORTS_SCRIPT.exists():
        logger.error(f"✗ send_reports.py not found at {SEND_REPORTS_SCRIPT}")
        return False
    
    logger.info(f"✓ Found send_reports.py")
    logger.info(f"✓ Python executable: {PYTHON_EXE}")
    logger.info(f"✓ Working directory: {SCRIPT_DIR}")
    logger.info("")
    
    # Try to create task
    logger.info("Attempting to create scheduled task...")
    logger.info("")
    
    success = False
    
    # Try PowerShell first (more reliable and feature-rich)
    try:
        success = create_task_via_powershell()
    except Exception as e:
        logger.warning(f"PowerShell method failed: {e}")
        logger.info("Falling back to schtasks method...")
        success = create_task_via_schtasks()
    
    if not success:
        logger.error("✗ Failed to create scheduled task")
        return False
    
    logger.info("")
    
    # List the task to verify
    logger.info("Verifying task creation...")
    list_scheduled_task()
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("✓ Task Scheduler Setup Complete!")
    logger.info("=" * 70)
    logger.info("")
    logger.info("IMPORTANT CONFIGURATION NOTES:")
    logger.info("-" * 70)
    logger.info(f"1. Task Name: {TASK_NAME}")
    logger.info(f"2. Schedule: Daily at {TASK_TIME} (12:00 AM)")
    logger.info(f"3. Run As: SYSTEM (won't be interrupted by shutdown)")
    logger.info("")
    logger.info("NEXT STEPS:")
    logger.info("-" * 70)
    logger.info("1. Update .env file with EMAIL_RECIPIENTS (comma-separated)")
    logger.info("   Example: EMAIL_RECIPIENTS=user1@company.com,user2@company.com")
    logger.info("")
    logger.info("2. Test the configuration:")
    logger.info(f"   python send_reports.py --mode test")
    logger.info("")
    logger.info("3. Monitor the logs directory for execution logs:")
    logger.info(f"   {SCRIPT_DIR / 'logs'}")
    logger.info("")
    logger.info("4. To view the task in Task Scheduler GUI:")
    logger.info("   taskmgr → Task Scheduler → Task Scheduler Library")
    logger.info(f"   Search for: {TASK_NAME}")
    logger.info("")
    logger.info("5. To REMOVE the task later:")
    logger.info(f"   python setup_task_scheduler.py --delete")
    logger.info("")
    logger.info("=" * 70)
    
    return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Windows Task Scheduler Setup for L2 Report Automation'
    )
    parser.add_argument('--delete', action='store_true',
                       help='Delete the scheduled task instead of creating it')
    parser.add_argument('--list', action='store_true',
                       help='List the scheduled task details')
    
    args = parser.parse_args()
    
    log_file = setup_logging()
    
    if args.delete:
        if check_admin_privileges():
            delete_scheduled_task()
        else:
            logger.error("Administrator privileges required to delete task")
    elif args.list:
        list_scheduled_task()
    else:
        success = main()
        sys.exit(0 if success else 1)
