---
name: scheduler
description: |
  Schedule recurring tasks via cron (Linux/Mac) or Task Scheduler (Windows).
  Use for daily briefings, weekly audits, periodic checks, and time-based
  automations. Supports one-time and recurring schedules.
---

# Scheduler Skill

Schedule recurring tasks for your AI Employee.

## Overview

This skill provides cross-platform scheduling:
- **Windows**: Task Scheduler integration
- **Linux/Mac**: Cron job integration
- **Python**: APScheduler for in-process scheduling

## Quick Start

### Schedule Daily Briefing (Windows)

```bash
python scheduler.py create \
  --name "Daily_Briefing" \
  --command "qwen" \
  --args "--cwd 'C:/Vault' -p 'Generate daily briefing'" \
  --schedule "daily" \
  --time "08:00"
```

### Schedule Weekly Audit (Linux/Mac)

```bash
python scheduler.py create \
  --name "Weekly_Audit" \
  --command "python" \
  --args "orchestrator.py /home/user/Vault" \
  --schedule "weekly" \
  --day "monday" \
  --time "07:00"
```

## Usage

### Create Scheduled Task

```bash
python scheduler.py create \
  --name "Task_Name" \
  --command "command_to_run" \
  --args "arguments" \
  --schedule "daily|weekly|monthly|once" \
  [--time "HH:MM"] \
  [--day "monday|tuesday|..."] \
  [--date "YYYY-MM-DD"]
```

### List Scheduled Tasks

```bash
python scheduler.py list
```

### Remove Scheduled Task

```bash
python scheduler.py remove --name "Task_Name"
```

### Run Task Now (Test)

```bash
python scheduler.py run --name "Task_Name"
```

## Schedule Options

### Daily

Run every day at specified time:

```bash
python scheduler.py create \
  --name "Morning_Briefing" \
  --command "qwen" \
  --schedule "daily" \
  --time "08:00"
```

### Weekly

Run on specific day(s) every week:

```bash
python scheduler.py create \
  --name "Monday_Audit" \
  --command "python" \
  --args "orchestrator.py /Vault" \
  --schedule "weekly" \
  --day "monday" \
  --time "07:00"
```

### Monthly

Run on specific date every month:

```bash
python scheduler.py create \
  --name "Monthly_Report" \
  --command "python" \
  --args "generate_report.py" \
  --schedule "monthly" \
  --day "1" \
  --time "09:00"
```

### One-Time

Run once at specific date/time:

```bash
python scheduler.py create \
  --name "Quarterly_Review" \
  --command "qwen" \
  --schedule "once" \
  --date "2026-03-31" \
  --time "17:00"
```

## Example Tasks

### Daily CEO Briefing (8 AM)

```bash
python scheduler.py create \
  --name "CEO_Briefing" \
  --command "qwen" \
  --args "-p 'Generate Monday Morning CEO Briefing'" \
  --schedule "daily" \
  --time "08:00"
```

### Hourly Email Check

```bash
python scheduler.py create \
  --name "Email_Check" \
  --command "python" \
  --args "gmail_watcher.py /Vault --once" \
  --schedule "hourly"
```

### Weekly Business Review (Monday 7 AM)

```bash
python scheduler.py create \
  --name "Weekly_Review" \
  --command "qwen" \
  --args "-p 'Review business goals and generate weekly report'" \
  --schedule "weekly" \
  --day "monday" \
  --time "07:00"
```

### Subscription Audit (1st of month)

```bash
python scheduler.py create \
  --name "Subscription_Audit" \
  --command "python" \
  --args "audit_subscriptions.py /Vault" \
  --schedule "monthly" \
  --day "1" \
  --time "09:00"
```

## Task Configuration

Tasks are stored in:
```
Vault/scheduler/tasks.json
```

Format:
```json
{
  "tasks": [
    {
      "name": "Daily_Briefing",
      "command": "qwen",
      "args": "-p 'Generate briefing'",
      "schedule": "daily",
      "time": "08:00",
      "enabled": true,
      "last_run": null,
      "next_run": "2026-01-08T08:00:00"
    }
  ]
}
```

## Output & Logging

Task execution logged to:
```
Vault/Logs/scheduler/YYYY-MM-DD.log
```

Log entry:
```json
{
  "timestamp": "2026-01-07T08:00:00Z",
  "task": "Daily_Briefing",
  "command": "qwen -p 'Generate briefing'",
  "status": "success",
  "duration_seconds": 45,
  "output": "Briefing generated successfully"
}
```

## Windows Task Scheduler

On Windows, tasks are registered with Task Scheduler:

### View Registered Tasks

```bash
schtasks /query /fo LIST /v | findstr "AI_Employee"
```

### Run Task Manually

```bash
schtasks /run /tn "AI_Employee_Daily_Briefing"
```

### Delete Task

```bash
schtasks /delete /tn "AI_Employee_Daily_Briefing" /f
```

## Linux/Mac Cron

On Linux/Mac, cron jobs are added to crontab:

### View Cron Jobs

```bash
crontab -l | grep AI_Employee
```

### Edit Cron Jobs

```bash
crontab -e
```

## Python API

```python
from scheduler import TaskScheduler

scheduler = TaskScheduler(vault_path="C:/Vault")

# Create daily task
scheduler.create_task(
    name="Daily_Briefing",
    command="qwen",
    args="-p 'Generate briefing'",
    schedule="daily",
    time="08:00"
)

# List tasks
tasks = scheduler.list_tasks()
for task in tasks:
    print(f"{task['name']}: {task['next_run']}")

# Run task now
scheduler.run_task("Daily_Briefing")

# Remove task
scheduler.remove_task("Daily_Briefing")
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task not running | Check scheduler service is running |
| Wrong time zone | Set TZ environment variable |
| Permission denied | Run as administrator |
| Command not found | Use full path to command |
| Task runs twice | Check for duplicate registrations |

## Best Practices

1. **Use descriptive names**: `Monday_Morning_Briefing` not `task1`
2. **Log everything**: Check logs for failures
3. **Test first**: Use `run` command before scheduling
4. **Set reasonable times**: Avoid middle of night
5. **Monitor failures**: Review logs daily

## Security Notes

- ⚠️ Don't schedule sensitive actions without approval
- ✅ Review scheduled tasks monthly
- ✅ Use service accounts for automated tasks
- ✅ Log all task executions
