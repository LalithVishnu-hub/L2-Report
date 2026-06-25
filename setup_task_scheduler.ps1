# PowerShell Script to Configure Task Scheduler for L2 Report
# Run this as Administrator to set up the task with proper settings

# Define variables
$taskName = "L2 Report Daily"
$taskFolder = "L2 Report"
$pythonScript = "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\L2_Report_Mail\send_l2_report_outlook_account.py"
$pythonExe = "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\.venv\Scripts\python.exe"
$venvActivate = "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\.venv\Scripts\Activate.ps1"
$workDir = "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "L2 Report Task Scheduler Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Create task action - uses python directly with venv
$action = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument """$pythonScript""" `
    -WorkingDirectory $workDir

Write-Host "✓ Task action created" -ForegroundColor Green

# Set task to run at 4:00 PM every day (16:00)
$trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At "4:00 PM"

Write-Host "✓ Daily trigger set for 4:00 PM" -ForegroundColor Green

# Create settings with all the necessary options
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Write-Host "✓ Task settings configured" -ForegroundColor Green

# Create the principal (run as user, not system)
$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType ServiceAccount `
    -RunLevel Highest

Write-Host "✓ Principal configured for $env:USERDOMAIN\$env:USERNAME" -ForegroundColor Green

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -TaskPath "\$taskFolder\" -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host ""
    Write-Host "Updating existing task: $taskName" -ForegroundColor Yellow
    Set-ScheduledTask -TaskName $taskName -TaskPath "\$taskFolder\" `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal
    Write-Host "✓ Task updated successfully" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Creating new task: $taskName" -ForegroundColor Yellow
    Register-ScheduledTask `
        -TaskName $taskName `
        -TaskPath "\$taskFolder\" `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Force | Out-Null
    Write-Host "✓ Task created successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Task Details:" -ForegroundColor Yellow
Write-Host "  Name: $taskName"
Write-Host "  Path: \$taskFolder\"
Write-Host "  Schedule: Daily at 4:00 PM"
Write-Host "  Run as: $env:USERDOMAIN\$env:USERNAME"
Write-Host "  Privileges: Highest"
Write-Host "  Battery: Allowed"
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Open Task Scheduler and verify the task appears"
Write-Host "2. Right-click task and select 'Run' to test it"
Write-Host "3. Check if report is generated and email is sent"
Write-Host "4. Check logs in: $workDir\logs\"
Write-Host ""
