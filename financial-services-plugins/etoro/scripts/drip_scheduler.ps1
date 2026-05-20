# Agent-DRIP Windows Scheduler Setup
$WorkingDirectory = "d:\Projects\Antigravity\Financial AI\financial-services-plugins\etoro\scripts"
$ScriptPath = Join-Path $WorkingDirectory "drip_handler.py"
$PythonPath = (Get-Command python).Source

# Define the action: Run Python with our script
$action = New-ScheduledTaskAction -Execute $PythonPath -Argument "`"$ScriptPath`"" -WorkingDirectory $WorkingDirectory

# Define the trigger: Every 4 hours, indefinitely
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 4)

# Register the task
$taskName = "Antigravity_AgentDRIP"
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Description "Automated Dividend Reinvestment for eToro Portfolio" -Force

Write-Host "---"
Write-Host "✅ Success: Windows Task '$taskName' has been registered."
Write-Host "---"
Write-Host "Your portfolio will now be checked for dividends every 4 hours."
Write-Host "You do NOT need to keep Antigravity open for this to work."
Write-Host "Logs are available at: $WorkingDirectory\drip_reconciliation.log"
