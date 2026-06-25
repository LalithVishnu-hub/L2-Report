# Fix Task Scheduler - reads time from .env and creates a robust task for L2 report email
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
    Write-Host "Administrator privileges are required. Requesting elevation..."
    try {
        $scriptPath = $MyInvocation.MyCommand.Path
        Start-Process -FilePath "powershell.exe" `
            -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `""$scriptPath`""" `
            -Verb RunAs `
            -ErrorAction Stop | Out-Null
        Write-Host "UAC prompt opened. Approve it to continue scheduler setup."
        exit 0
    }
    catch {
        Write-Host "ERROR: Could not elevate automatically: $_"
        Write-Host "Please run PowerShell as Administrator and re-run this script."
        exit 1
    }
}

Write-Host "Admin privileges verified"
Write-Host ""

$taskName = "L2 Project Dashboard Report"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$envPath = Join-Path $projectRoot ".env"
$batchFilePath = Join-Path $scriptDir "run_l2_report.bat"
$runAsUser = "$env:USERDOMAIN\$env:USERNAME"

if (-not (Test-Path $batchFilePath)) {
    Write-Host "ERROR: Batch file not found: $batchFilePath"
    exit 1
}

# Remove old task if it exists
Write-Host "Checking for existing task..."
$taskExists = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($taskExists) {
    Write-Host "Removing old task..."
    try {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction Stop
        Write-Host "Old task removed successfully"
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
$schedulerHour = 0
$schedulerMinute = 30

if (Test-Path $envPath) {
    $envContent = Get-Content $envPath -Raw

    if ($envContent -match 'SCHEDULER_HOUR\s*=\s*(\d+)') {
        $schedulerHour = [int]$matches[1]
    }

    if ($envContent -match 'SCHEDULER_MINUTE\s*=\s*(\d+)') {
        $schedulerMinute = [int]$matches[1]
    }

    if ($schedulerHour -lt 0 -or $schedulerHour -gt 23) {
        Write-Host "WARNING: Invalid SCHEDULER_HOUR in .env. Using default 00."
        $schedulerHour = 0
    }

    if ($schedulerMinute -lt 0 -or $schedulerMinute -gt 59) {
        Write-Host "WARNING: Invalid SCHEDULER_MINUTE in .env. Using default 30."
        $schedulerMinute = 30
    }

    Write-Host "Read from .env: Hour=$schedulerHour, Minute=$schedulerMinute"
}
else {
    Write-Host "WARNING: .env file not found, using default 12:30 AM"
}

$scheduledTime = Get-Date -Hour $schedulerHour -Minute $schedulerMinute -Second 0
$timeDisplay = $scheduledTime.ToString("hh:mm tt")

Write-Host "Creating new task scheduled for $timeDisplay daily..."

try {
    # Use cmd.exe to reliably execute batch files from Task Scheduler
    $taskAction = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"`"$batchFilePath`"`"" -WorkingDirectory $scriptDir -ErrorAction Stop

    # Daily trigger at configured time
    $taskTrigger = New-ScheduledTaskTrigger -Daily -At $scheduledTime -ErrorAction Stop

    # Run in user context so Outlook profile is available
    $taskPrincipal = New-ScheduledTaskPrincipal -UserId $runAsUser -LogonType Interactive -RunLevel Highest -ErrorAction Stop

    # -WakeToRun wakes system from sleep. Do NOT use StartWhenAvailable (no missed-run catch-up behavior).
    $taskSettings = New-ScheduledTaskSettingsSet `
        -WakeToRun `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -RunOnlyIfNetworkAvailable `
        -MultipleInstances IgnoreNew `
        -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
        -ErrorAction Stop

    Register-ScheduledTask -TaskName $taskName `
        -Action $taskAction `
        -Trigger $taskTrigger `
        -Principal $taskPrincipal `
        -Settings $taskSettings `
        -Description "Generates and sends L2 Project Dashboard report via Outlook email at $timeDisplay daily" `
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
    $taskInfo = Get-ScheduledTask -TaskName $taskName -ErrorAction Stop | Get-ScheduledTaskInfo -ErrorAction Stop
    Write-Host "Task Name: $taskName"
    Write-Host "Run As User: $runAsUser"
    Write-Host "Schedule: Daily at $timeDisplay"
    Write-Host "Action: $batchFilePath"
    Write-Host "Wake from sleep: Enabled"
    Write-Host "Missed run catch-up after shutdown/off: Disabled"
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
Write-Host "Notes:"
Write-Host "1) During SLEEP, the task can wake the machine and run if wake timers are allowed in Windows power settings."
Write-Host "2) During SHUTDOWN/OFF state, no local Windows task can run at the exact schedule time."
Write-Host "3) Outlook-based sending requires your user session (interactive profile)."
Write-Host ""
Write-Host "Log files will be saved to: $projectRoot\logs\email_delivery_*.log"
Write-Host ""