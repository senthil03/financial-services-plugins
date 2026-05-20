# Market Volatility & Commodity Price Alerts Scheduler
$WorkingDirectory = "d:\Projects\Antigravity\Financial AI\financial-services-plugins\etoro\scripts"
$ScriptPath = Join-Path $WorkingDirectory "market_alerts_monitor.py"
$PythonPath = (Get-Command python).Source

# Define the execution action
$action = New-ScheduledTaskAction -Execute $PythonPath -Argument "`"$ScriptPath`"" -WorkingDirectory $WorkingDirectory

# Trigger: Every 1 hour, indefinitely
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)

# Register the Task in Windows Task Scheduler
$taskName = "Antigravity_Market_Alerts"
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Description "Automated hourly scans for portfolio equity volatility, commodities, and technical buy entry triggers." -Force

Write-Host "---"
Write-Host "✅ Success: Windows Task '$taskName' has been registered."
Write-Host "---"
Write-Host "The monitor will now perform hourly scans 24/7 for portfolio changes, gold, and silver."
