# AI Employee - Silver Tier Setup Guide

Complete setup instructions for the Silver Tier implementation with Gmail and LinkedIn integration.

## Silver Tier Features

| Feature | Status | Description |
|---------|--------|-------------|
| **Gmail Watcher** | ✅ | Monitor Gmail for new emails |
| **LinkedIn Watcher** | ✅ | Monitor LinkedIn for messages/notifications |
| **LinkedIn Poster** | ✅ | Auto-post to LinkedIn |
| **Plan Creator** | ✅ | Automatic plan generation |
| **Approval Workflow** | ✅ | Human-in-the-loop approvals |
| **Scheduler** | ✅ | Task scheduling (cron/Task Scheduler) |
| **Email Sender** | ✅ | Send emails via SMTP/Gmail API |

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.13+ | Watcher scripts |
| Qwen Code | Latest | Reasoning engine |
| Obsidian | v1.10.6+ | Dashboard/GUI |
| Node.js | v24+ LTS | MCP servers (optional) |

### Python Packages

```bash
# Core dependencies
pip install watchdog

# Gmail API
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# LinkedIn (Playwright)
pip install playwright
playwright install
```

## Step 1: Gmail API Setup

### 1.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (e.g., "AI Employee")
3. Enable **Gmail API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

### 1.2 Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: **Web application**
4. Add authorized redirect URI: `http://localhost:8080/`
5. Download the credentials as `credentials.json`
6. Place `credentials.json` in the project root:
   ```
   Personal_AI_Employee_FTEs/credentials.json
   ```

### 1.3 First-Time Gmail Authentication

Run the Gmail watcher once to authenticate:

```bash
cd AI_Employee_Vault/scripts
python gmail_watcher.py "../" --once
```

This will:
1. Open a browser window
2. Ask you to sign in to Google
3. Request Gmail permissions
4. Save a `token.json` file for future use

## Step 2: LinkedIn Setup

### 2.1 Install Playwright

```bash
pip install playwright
playwright install chromium
```

### 2.2 LinkedIn Login

Save your LinkedIn session:

```bash
cd AI_Employee_Vault/scripts
python linkedin_watcher.py "../" --login
```

This will:
1. Open a browser window
2. You log in to LinkedIn manually
3. Press Enter after logged in
4. Session cookies are saved

### 2.3 Test LinkedIn Watcher

```bash
python linkedin_watcher.py "../" --once
```

## Step 3: Verify Installation

### Check All Dependencies

```bash
python -c "
import sys
try:
    from google.oauth2.credentials import Credentials
    print('✅ Gmail API: OK')
except:
    print('❌ Gmail API: Not installed')

try:
    from playwright.sync_api import sync_playwright
    print('✅ Playwright: OK')
except:
    print('❌ Playwright: Not installed')

try:
    import watchdog
    print('✅ Watchdog: OK')
except:
    print('❌ Watchdog: Not installed')
"
```

### Test File System Watcher

```bash
# Start watcher
python filesystem_watcher.py "../" "../DropFolder"

# In another terminal, create a test file
echo "Test message" > "../DropFolder/test.txt"

# Check if action file was created
dir "..\Needs_Action"
```

### Test Gmail Watcher

```bash
python gmail_watcher.py "../" --once
```

Expected output:
```
📧 Gmail Watcher started
✅ Gmail authenticated successfully
Found X new message(s)
  ✅ Created: EMAIL_xxx_subject.md
```

### Test LinkedIn Watcher

```bash
python linkedin_watcher.py "../" --once
```

Expected output:
```
🔗 LinkedIn Watcher started
Found X new item(s)
  ✅ Created: LINKEDIN_xxx_message.md
```

## Step 4: Start All Watchers

### Option A: Manual Start (Testing)

Open three terminal windows:

**Terminal 1 - File System Watcher:**
```bash
cd AI_Employee_Vault/scripts
python filesystem_watcher.py "../" "../DropFolder"
```

**Terminal 2 - Gmail Watcher:**
```bash
cd AI_Employee_Vault/scripts
python gmail_watcher.py "../"
```

**Terminal 3 - LinkedIn Watcher:**
```bash
cd AI_Employee_Vault/scripts
python linkedin_watcher.py "../"
```

### Option B: Windows Batch File

Create `start_watchers.bat`:

```batch
@echo off
start cmd /k "cd AI_Employee_Vault\scripts && python filesystem_watcher.py ../ ../DropFolder"
start cmd /k "cd AI_Employee_Vault\scripts && python gmail_watcher.py ../"
start cmd /k "cd AI_Employee_Vault\scripts && python linkedin_watcher.py ../"
echo All watchers started!
```

Run:
```bash
start_watchers.bat
```

### Option C: PM2 (Production)

```bash
# Install PM2
npm install -g pm2

# Start watchers
pm2 start filesystem_watcher.py --interpreter python --cwd "AI_Employee_Vault/scripts" -- "../" "../DropFolder"
pm2 start gmail_watcher.py --interpreter python --cwd "AI_Employee_Vault/scripts" -- "../"
pm2 start linkedin_watcher.py --interpreter python --cwd "AI_Employee_Vault/scripts" -- "../"

# Save configuration
pm2 save

# Start on boot
pm2 startup
```

## Step 5: Process Items with Qwen Code

### Run Orchestrator

```bash
cd AI_Employee_Vault/scripts
python orchestrator.py "../"
```

This will:
1. Check `Needs_Action/` for new items
2. Create plans in `Plans/`
3. Update `Dashboard.md`
4. Prepare items for Qwen Code processing

### Use Qwen Code

```bash
cd AI_Employee_Vault
qwen
```

Then prompt:
```
Check the Plans folder and process all pending items.
Follow the Company_Handbook.md for rules of engagement.
Create approval requests for sensitive actions.
```

## Step 6: Post to LinkedIn (Optional)

### Test LinkedIn Posting

```bash
cd .qwen/skills/linkedin-poster
python linkedin_poster.py post --content "Testing AI Employee Silver Tier! #AI #Automation"
```

### Schedule a Post

```bash
python linkedin_poster.py schedule \
  --content "Monday motivation: Automate your business with AI!" \
  --time "2026-01-13T09:00:00"
```

## Step 7: Set Up Scheduler (Optional)

### Schedule Daily Briefing (Windows)

```bash
python scheduler.py create \
  --vault "../" \
  --name "Daily_Briefing" \
  --command "qwen" \
  --args "-p 'Generate daily briefing'" \
  --schedule "daily" \
  --time "08:00"
```

### Schedule Weekly Review

```bash
python scheduler.py create \
  --vault "../" \
  --name "Weekly_Review" \
  --command "qwen" \
  --args "-p 'Review business goals and generate weekly report'" \
  --schedule "weekly" \
  --day "monday" \
  --time "07:00"
```

## Folder Structure

```
Personal_AI_Employee_FTEs/
├── credentials.json           # Gmail API credentials
├── AI_Employee_Vault/
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Business_Goals.md
│   ├── scripts/
│   │   ├── base_watcher.py
│   │   ├── filesystem_watcher.py
│   │   ├── gmail_watcher.py
│   │   ├── linkedin_watcher.py
│   │   ├── orchestrator.py
│   │   └── requirements.txt
│   ├── Needs_Action/         # New items from watchers
│   ├── Plans/                # Generated action plans
│   ├── Pending_Approval/     # Awaiting human approval
│   ├── Approved/             # Approved actions
│   ├── Done/                 # Completed tasks
│   └── Logs/                 # System logs
└── .qwen/skills/
    ├── email-sender/
    ├── approval-workflow/
    ├── scheduler/
    ├── plan-creator/
    ├── linkedin-poster/
    └── browsing-with-playwright/
```

## Troubleshooting

### Gmail Watcher Issues

**Error: Credentials not found**
- Ensure `credentials.json` is in project root
- Check file permissions

**Error: Token expired**
- Delete `token.json` and re-authenticate
- Run: `python gmail_watcher.py "../" --once`

**Error: Gmail API not enabled**
- Go to Google Cloud Console
- Enable Gmail API for your project

### LinkedIn Watcher Issues

**Error: Not logged in**
- Run: `python linkedin_watcher.py "../" --login`
- Complete login in browser

**Error: Playwright not installed**
- Run: `pip install playwright && playwright install chromium`

**Error: Session expired**
- Re-run login command
- Session cookies expire after ~2 weeks

### Orchestrator Issues

**Error: No items processed**
- Check watchers are running
- Verify `Needs_Action/` folder has items
- Check logs in `Logs/` folder

## Daily Workflow

### Morning (8:00 AM)

1. Check Dashboard.md for overnight activity
2. Review any pending approvals in `Pending_Approval/`
3. Run orchestrator: `python orchestrator.py "../"`
4. Process items with Qwen Code

### Throughout Day

- Watchers automatically detect new items
- Action files created in `Needs_Action/`
- Plans generated automatically

### Evening (6:00 PM)

1. Review completed items in `Done/`
2. Check logs for any errors
3. Approve/reject pending actions

## Security Best Practices

1. **Never commit credentials**: Add to `.gitignore`
   ```
   credentials.json
   token.json
   .linkedin_session/
   *.log
   ```

2. **Review approvals**: Always review before approving sensitive actions

3. **Monitor logs**: Check `Logs/` folder daily

4. **Rotate credentials**: Update Gmail API credentials monthly

## Next Steps (Gold Tier)

After mastering Silver Tier:
- Add WhatsApp watcher
- Integrate Odoo accounting
- Implement Ralph Wiggum loop
- Add error recovery
- Weekly CEO Briefing generation

---

*Silver Tier Implementation - AI Employee v2.0*
