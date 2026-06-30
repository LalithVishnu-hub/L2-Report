# PowerShell Script to Configure Task Scheduler for L2 Report PVT
# Run this as Administrator to set up the task with proper settings
# Sends PVT report on weekdays at 8:20 AM

# Define variables
$taskName = "L2 Report Daily - PVT"
$taskFolder = "L2 Report"
$pythonScript = "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\L2_Report_Mail\send_l2_report_outlook_account.py"
$pythonExe = "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\.venv\Scripts\python.exe"
$workDir = "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "L2 Report Task Scheduler Setup - PVT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "This task runs on weekdays at 8:20 AM" -ForegroundColor Yellow
Write-Host " "

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select Run as Administrator" -ForegroundColor Yellow
    exit 1
}

# Create task action - uses python directly with venv and --report-type pvt parameter
$argumentString = "$pythonScript --report-type pvt"
$action = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument $argumentString `
    -WorkingDirectory $workDir

Write-Host "[+] Task action created (--report-type pvt parameter added)" -ForegroundColor Green

# Set task to run at 8:20 AM on weekdays (Monday-Friday)
$trigger = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek @('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday') `
    -At "8:20 AM"

Write-Host "[+] Weekly trigger set for weekdays at 8:20 AM (Mon-Fri)" -ForegroundColor Green

# Create settings with all the necessary options
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Write-Host "[+] Task settings configured" -ForegroundColor Green

# Create the principal (run as user, whether logged on or not)
$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Highest

Write-Host "[+] Principal configured (run whether user is logged on or not)" -ForegroundColor Green

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
    Write-Host "Schedule: Weekdays Mon-Fri at 8:20 AM" -ForegroundColor White
    Write-Host "Report Type: PVT" -ForegroundColor White
    Write-Host "Script: $pythonScript" -ForegroundColor White
    Write-Host "Working Directory: $workDir" -ForegroundColor White
    Write-Host " "
    Write-Host "Note: Make sure EMAIL_TO_PVT and EMAIL_CC_PVT are configured in .env" -ForegroundColor Yellow
    Write-Host " "
}
catch {
    Write-Host "ERROR: Failed to register task" -ForegroundColor Red
    Write-Host "$_" -ForegroundColor Red
    exit 1
}

Write-Host "Setup completed successfully!" -ForegroundColor Green
