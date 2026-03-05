# Quick Start - AI Employee Silver Tier

## What's Working ✅

1. **Gmail Watcher** - Fetches emails from Gmail
2. **File System Watcher** - Monitors drop folder
3. **Orchestrator** - Creates plans for Qwen Code
4. **Qwen Code Integration** - Processes tasks

## Daily Workflow

### Morning Check (8:00 AM)

```bash
# 1. Go to project folder
cd C:\GIAIC Disk\Q4-Nov-2025\Hackathon-q4\Personal_AI_Employee_FTEs

# 2. Check Gmail for new emails
cd AI_Employee_Vault/scripts
python gmail_watcher.py "../" --once

# 3. Process all pending items
python orchestrator.py "../"

# 4. Use Qwen Code to handle tasks
cd ..
qwen
```

Then prompt Qwen:
```
Check the Plans folder and process all pending items.
Follow Company_Handbook.md for rules.
Draft responses for emails that need replies.
```

### Throughout the Day

**Drop files for processing:**
```bash
# Create a text file with any task
echo "Follow up with client about invoice" > DropFolder/task.txt
```

File System Watcher will detect it and create an action file automatically.

### Evening Review (6:00 PM)

```bash
# Check what was completed
dir AI_Employee_Vault\Done

# Review logs
type AI_Employee_Vault\Logs\*.log
```

## LinkedIn Integration

**Best Method: Email Notifications**

1. Enable LinkedIn email notifications:
   - https://www.linkedin.com/mynetwork/management/settings/
   - Set email frequency to "Immediately"

2. Gmail Watcher will fetch them automatically

**For Posting:**
1. Ask Qwen to draft a post
2. Copy and paste manually to LinkedIn

## Commands Reference

| Command | Purpose |
|---------|---------|
| `python gmail_watcher.py "../" --once` | Check Gmail once |
| `python gmail_watcher.py "../"` | Run Gmail watcher continuously |
| `python filesystem_watcher.py "../" "../DropFolder"` | Monitor drop folder |
| `python orchestrator.py "../"` | Process pending items |
| `python linkedin_poster.py login` | Login to LinkedIn |
| `python linkedin_poster.py post --content "..."` | Post to LinkedIn |

## Folders

| Folder | Purpose |
|--------|---------|
| `Needs_Action/` | New items to process |
| `Plans/` | Generated action plans |
| `Pending_Approval/` | Awaiting your approval |
| `Approved/` | Ready for execution |
| `Done/` | Completed items |
| `Logs/` | System logs |

## Need Help?

- **Gmail not working?** Run: `python gmail_watcher.py "../" --once` to re-authenticate
- **LinkedIn session expired?** Run: `python linkedin_poster.py login`
- **Check logs:** `type AI_Employee_Vault\Logs\*.log`

---

*Silver Tier - AI Employee v2.0*
