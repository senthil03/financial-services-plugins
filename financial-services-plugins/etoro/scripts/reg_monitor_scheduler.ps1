# Regulatory News Monitor Scheduler
$WorkingDirectory = "d:\Projects\Antigravity\Financial AI\financial-services-plugins\etoro\scripts"
$ScriptPath = Join-Path $WorkingDirectory "regulatory_news_monitor.py"
$PythonPath = (Get-Command python).Source

# Define the action
$action = New-ScheduledTaskAction -Execute $PythonPath -Argument "`"$ScriptPath`"" -WorkingDirectory $WorkingDirectory

# Define triggers: 8:00 AM and 5:00 PM Daily
$trigger1 = New-ScheduledTaskTrigger -Daily -At 8:00am
$trigger2 = New-ScheduledTaskTrigger -Daily -At 5:00pm

# Register the task
$taskName = "Antigravity_Regulatory_Monitor"
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger @($trigger1, $trigger2) -Description "Automated Regulatory News Monitoring for VST and AI-Power Catalysts" -Force

Write-Host "---"
Write-Host "✅ Success: Windows Task '$taskName' has been registered."
Write-Host "---"
Write-Host "The monitor will now scan for Vistra/BTM news every day at 8:00 AM and 5:00 PM."
