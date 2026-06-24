# Fix Task Scheduler - Reads time from .env configuration
# Run with Administrator privileges

Write-Host "=========================================="
Write-Host "L2 Report Scheduler Setup"
Write-Host "=========================================="
Write-Host ""

# Check if running as Administrator
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object System.Security.Principal.WindowsPrincipal($currentUser)
$adminRole = [System.Security.Principal.WindowsBuiltInRole]::Administrator

if (-not $principal.IsInRole($adminRole)) {
    Write-Host "ERROR: This script requires Administrator privileges!"
    Write-Host "Please run PowerShell as Administrator and try again."
    exit 1
}

Write-Host "Admin privileges verified"
Write-Host ""

# Remove old task if it exists
Write-Host "Checking for existing task..."
$taskExists = Get-ScheduledTask -TaskName "L2 Project Dashboard Report" -ErrorAction SilentlyContinue
if ($taskExists) {
    Write-Host "Removing old task..."
    try {
        Unregister-ScheduledTask -TaskName "L2 Project Dashboard Report" -Confirm:$false -ErrorAction Stop
        Write-Host "Old task removed successfully"
        Start-Sleep -Seconds 1
    }
    catch {
        Write-Host "ERROR: Could not remove old task: $_"
        exit 1
    }
}
else {
    Write-Host "No existing task found"
}

Write-Host ""

# Read scheduler time from .env file
$envPath = "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\.env"
$schedulerHour = 0
$schedulerMinute = 30

if (Test-Path $envPath) {
    $envContent = Get-Content $envPath -Raw
    
    # Extract SCHEDULER_HOUR
    if ($envContent -match 'SCHEDULER_HOUR\s*=\s*(\d+)') {
        $schedulerHour = [int]$matches[1]
    }
    
    # Extract SCHEDULER_MINUTE
    if ($envContent -match 'SCHEDULER_MINUTE\s*=\s*(\d+)') {
        $schedulerMinute = [int]$matches[1]
    }
    
    Write-Host "Read from .env: Hour=$schedulerHour, Minute=$schedulerMinute"
}
else {
    Write-Host "WARNING: .env file not found, using default 12:30 AM"
}

# Format time as HH:MM:SS
$scheduledTime = "{0:00}:{1:00}:00" -f $schedulerHour, $schedulerMinute
$timeDisplay = if ($schedulerHour -lt 12) { 
    "{0:00}:{1:00} AM" -f $schedulerHour, $schedulerMinute 
} 
else { 
    if ($schedulerHour -eq 12) {
        "{0:00}:{1:00} PM" -f $schedulerHour, $schedulerMinute
    } else {
        "{0:00}:{1:00} PM" -f ($schedulerHour - 12), $schedulerMinute
    }
}

Write-Host "Creating new task scheduled for $timeDisplay daily..."

$batchFilePath = "C:\Users\LalithVishnu\Desktop\Project Dashboard-L2 SQL DB\L2_Report_Mail\run_l2_report.bat"

try {
    $taskAction = New-ScheduledTaskAction -Execute $batchFilePath -ErrorAction Stop
    $taskTrigger = New-ScheduledTaskTrigger -Daily -At $scheduledTime -ErrorAction Stop
    $taskSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable -ErrorAction Stop
    
    Register-ScheduledTask -TaskName "L2 Project Dashboard Report" `
        -Action $taskAction `
        -Trigger $taskTrigger `
        -Settings $taskSettings `
        -Description "Generates and sends L2 Project Dashboard report via Outlook email at $timeDisplay daily" `
        -RunLevel Highest `
        -Force `
        -ErrorAction Stop

    Write-Host "[OK] Task scheduler created successfully!"
}
catch {
    Write-Host "ERROR: Failed to create task: $_"
    exit 1
}

Write-Host ""
Write-Host "=========================================="
Write-Host "Task Details:"
Write-Host "=========================================="

try {
    $taskInfo = Get-ScheduledTask -TaskName "L2 Project Dashboard Report" -ErrorAction Stop | Get-ScheduledTaskInfo -ErrorAction Stop
    Write-Host "Task Name: L2 Project Dashboard Report"
    Write-Host "Schedule: Daily at $timeDisplay ($scheduledTime)"
    Write-Host "Status: $($taskInfo.State)"
    Write-Host "Next Run: $($taskInfo.NextRunTime)"
    Write-Host "Last Run: $($taskInfo.LastRunTime)"
    Write-Host "Last Result: $($taskInfo.LastTaskResult)"
}
catch {
    Write-Host "Could not retrieve task details: $_"
}

Write-Host ""
Write-Host "=========================================="
Write-Host "[OK] Setup complete!"
Write-Host "=========================================="
Write-Host ""
Write-Host "Task will run automatically at $timeDisplay every day."
Write-Host "Time configured from .env: SCHEDULER_HOUR=$schedulerHour, SCHEDULER_MINUTE=$schedulerMinute"
Write-Host "Log files will be saved to: logs/email_delivery_*.log"
Write-Host ""
