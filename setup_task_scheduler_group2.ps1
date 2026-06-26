# PowerShell Script to Configure Task Scheduler for L2 Report Group 2
# Run this as Administrator to set up the task with proper settings
# Sends to secondary contact group on weekdays at 8:30 AM

# Define variables
$taskName = "L2 Report Daily - Group 2"
$taskFolder = "L2 Report"
$pythonScript = "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\L2_Report_Mail\send_l2_report_outlook_account.py"
$pythonExe = "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\.venv\Scripts\python.exe"
$workDir = "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "L2 Report Task Scheduler Setup - Group 2" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "This task runs on weekdays at 8:30 AM" -ForegroundColor Yellow
Write-Host " "

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select Run as Administrator" -ForegroundColor Yellow
    exit 1
}

# Create task action - uses python directly with venv and --group parameter
$argumentString = "$pythonScript --group group2"
$action = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument $argumentString `
    -WorkingDirectory $workDir

Write-Host "[+] Task action created (Group 2 parameter added)" -ForegroundColor Green

# Set task to run at 8:30 AM on weekdays (Monday-Friday)
$trigger = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek @('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday') `
    -At "8:30 AM"

Write-Host "[+] Weekly trigger set for weekdays at 8:30 AM (Mon-Fri)" -ForegroundColor Green

# Create settings with all the necessary options
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Write-Host "[+] Task settings configured" -ForegroundColor Green

# Create the principal (run as user, not system)
$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType ServiceAccount `
    -RunLevel Highest

Write-Host "[+] Principal configured (running as current user)" -ForegroundColor Green

# Register the task
try {
    # First, check if task already exists and remove it
    $existingTask = Get-ScheduledTask -TaskName $taskName -TaskPath "\L2 Report\" -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Host "Removing existing task..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $taskName -TaskPath "\L2 Report\" -Confirm:$false
        Start-Sleep -Seconds 1
    }
    
    # Register new task
    Register-ScheduledTask `
        -TaskName $taskName `
        -TaskPath "\L2 Report\" `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Force | Out-Null
    
    Write-Host "[+] Task registered successfully" -ForegroundColor Green
    
    # Get task details
    Write-Host " "
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Task Successfully Created!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Task Name: $taskName" -ForegroundColor White
    Write-Host "Task Path: \L2 Report\" -ForegroundColor White
    Write-Host "Schedule: Weekdays Mon-Fri at 8:30 AM" -ForegroundColor White
    Write-Host "Contact Group: Group 2" -ForegroundColor White
    Write-Host "Script: $pythonScript" -ForegroundColor White
    Write-Host "Working Directory: $workDir" -ForegroundColor White
    Write-Host " "
    Write-Host "Note: Make sure EMAIL_TO_GROUP2 and EMAIL_CC_GROUP2 are configured in .env" -ForegroundColor Yellow
    Write-Host " "
}
catch {
    Write-Host "ERROR: Failed to register task" -ForegroundColor Red
    Write-Host "$_" -ForegroundColor Red
    exit 1
}

Write-Host "Setup completed successfully!" -ForegroundColor Green
