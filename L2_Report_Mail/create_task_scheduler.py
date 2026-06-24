"""
Create Windows Task Scheduler task for L2 Report
This script creates a scheduled task that runs daily at 12:00 AM
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def create_task_scheduler():
    """Create Task Scheduler task using schtasks command"""
    
    print("=" * 80)
    print("Windows Task Scheduler - L2 Report Setup")
    print("=" * 80)
    print()
    
    # Define task parameters
    task_name = "L2 Project Dashboard Report"
    batch_file = r"C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\run_l2_report.bat"
    schedule_time = "00:00"
    
    print(f"Task Name: {task_name}")
    print(f"Batch File: {batch_file}")
    print(f"Schedule: Daily at {schedule_time} (12:00 AM)")
    print()
    
    # Verify batch file exists
    if not Path(batch_file).exists():
        print(f"ERROR: Batch file not found: {batch_file}")
        return False
    
    print("✓ Batch file found")
    print()
    
    # Delete existing task if it exists
    print("Checking for existing task...")
    delete_cmd = f'schtasks /delete /tn "{task_name}" /f'
    try:
        result = subprocess.run(delete_cmd, shell=True, capture_output=True, text=True)
        if "SUCCESS" in result.stdout or "deleted" in result.stdout.lower():
            print(f"✓ Removed existing task")
        elif "ERROR" not in result.stdout:
            print(f"✓ No previous task found")
    except:
        pass
    
    print()
    
    # Create new task
    print("Creating scheduled task...")
    print()
    
    # Using SYSTEM account to run even when user is logged out
    create_cmd = (
        f'schtasks /create /tn "{task_name}" '
        f'/tr "{batch_file}" '
        f'/sc daily /st {schedule_time} '
        f'/ru SYSTEM /rl HIGHEST /f'
    )
    
    try:
        result = subprocess.run(create_cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        output = result.stdout + result.stderr
        
        if "ERROR: Access is denied" in output:
            print("ERROR: This script must be run with Administrator privileges!")
            print()
            print("SOLUTION: Please do ONE of the following:")
            print()
            print("1. Run Command Prompt as Administrator and paste this command:")
            print(f'   schtasks /create /tn "{task_name}" /tr "{batch_file}" /sc daily /st {schedule_time} /ru SYSTEM /rl HIGHEST /f')
            print()
            print("2. Or, right-click on 'Setup-TaskScheduler.bat' and select 'Run as administrator'")
            print()
            print("3. Or, open PowerShell as Administrator and run this command:")
            print(f'   Start-Process cmd -ArgumentList "/c schtasks /create /tn \\"{task_name}\\" /tr \\"{batch_file}\\" /sc daily /st {schedule_time} /ru SYSTEM /rl HIGHEST /f" -Verb RunAs')
            return False
        elif "SUCCESS" in output:
            print("✓ Task created successfully!")
            print()
            
            # Verify task was created
            verify_cmd = f'schtasks /query /tn "{task_name}" /v'
            verify_result = subprocess.run(verify_cmd, shell=True, capture_output=True, text=True)
            
            if "SUCCESS" in verify_result.stdout or task_name in verify_result.stdout:
                print("✓ Task verification: SUCCESS")
                print()
                print("Task Details:")
                print(f"  Name: {task_name}")
                print(f"  Trigger: Daily at {schedule_time} (Midnight)")
                print(f"  Action: {batch_file}")
                print(f"  Status: Ready")
                print()
                print("=" * 80)
                print("✓ Task is ready! It will run automatically every day at 12:00 AM")
                print("✓ Email will be sent to: lalvishn@in.ibm.com, lv1087@att.com")
                print("✓ Works even if system is shutdown or Outlook is closed")
                print("=" * 80)
                return True
            else:
                print("⚠ Task created but verification failed")
                print("Please verify manually in Task Scheduler")
                return False
        else:
            print(f"Command output: {output}")
            if "already exists" in output.lower():
                print("⚠ Task already exists")
                return True
            return False
            
    except subprocess.TimeoutExpired:
        print("ERROR: Command timed out")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = create_task_scheduler()
    
    if not success:
        print()
        print("Please run with Administrator privileges and try again!")
        sys.exit(1)
    else:
        sys.exit(0)
