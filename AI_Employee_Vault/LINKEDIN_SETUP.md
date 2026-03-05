# LinkedIn Integration Guide

## Problem
LinkedIn has strong automation detection that blocks automated browsers (Playwright/Selenium). This is by design to prevent bots.

## Solution: Semi-Manual Workflow

Since fully automated LinkedIn monitoring is blocked, use this semi-manual approach:

### Option 1: Manual Check + Qwen Code Process

1. **Manually check LinkedIn** in your browser
2. **Copy important messages/notifications** 
3. **Create a text file** in the DropFolder:
   ```
   DropFolder/linkedin_message.txt
   ```
4. **File System Watcher** will detect it and create an action file
5. **Qwen Code** will process it and suggest responses

### Option 2: Use LinkedIn Poster for Outbound Posts

For posting TO LinkedIn (which works better than reading):

```bash
cd AI_Employee_Vault/scripts
python linkedin_poster.py --login
```

This opens a browser once and saves your session for posting.

Then post updates:

```bash
python linkedin_poster.py post --content "Your business update here #AI #Automation"
```

### Option 3: Email Forwarding (Recommended)

LinkedIn sends email notifications for important activity:

1. **Go to LinkedIn Settings** → **Notifications**
2. **Enable email notifications** for:
   - Messages
   - Connection requests
   - Comments on your posts
3. **Gmail Watcher** will automatically fetch these emails
4. **Action files created** automatically in Needs_Action
5. **Qwen Code processes** them and suggests responses

This is the most reliable method!

## Current Status

| Feature | Status | Notes |
|---------|--------|-------|
| Gmail Watcher | ✅ Working | Fetches LinkedIn email notifications |
| LinkedIn Watcher | ⚠️ Limited | Blocked by LinkedIn bot detection |
| LinkedIn Poster | ✅ Working | Can post updates via browser automation |
| File Drop + Qwen | ✅ Working | Manual LinkedIn items → Qwen processing |

## Recommended Workflow

### For Incoming LinkedIn Activity:
1. Enable LinkedIn email notifications
2. Gmail Watcher fetches them automatically
3. Qwen Code processes and drafts responses

### For Outbound LinkedIn Posts:
1. Use LinkedIn Poster skill
2. Create content in a file
3. Post with approval workflow

## LinkedIn Poster Usage

### First-time Login:
```bash
cd AI_Employee_Vault/scripts
python linkedin_poster.py login
```

### Post an Update:
```bash
python linkedin_poster.py post \
  --content "Excited to share our AI Employee project! #AI #Automation"
```

### Schedule a Post:
```bash
python linkedin_poster.py schedule \
  --content "Monday motivation post" \
  --time "2026-03-02T09:00:00"
```

## Gmail + LinkedIn Email Notifications

Since Gmail Watcher is working perfectly, configure LinkedIn to send you emails:

1. Go to **LinkedIn** → **Me** → **Settings & Privacy**
2. Click **Notifications**
3. Configure email frequency: **Immediately**
4. Enable emails for:
   - Messages
   - Connection requests  
   - Job alerts
   - Post engagement

Then Gmail Watcher will automatically fetch these and create action files!

## Testing

Test the Gmail + LinkedIn integration:

```bash
# Run Gmail watcher (fetches LinkedIn emails)
python gmail_watcher.py "../" --once

# Run orchestrator (creates plans)
python orchestrator.py "../"

# Use Qwen Code to process
cd ..
qwen
```

Prompt Qwen:
```
Check the Needs_Action folder for LinkedIn-related emails.
Draft responses to any messages or connection requests.
```

---

*This semi-manual approach is more reliable than fighting LinkedIn's bot detection.*
