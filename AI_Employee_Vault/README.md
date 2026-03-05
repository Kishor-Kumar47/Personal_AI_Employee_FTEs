# AI Employee - Bronze Tier

A local-first, autonomous AI employee powered by Qwen Code and Obsidian.

## Overview

This Bronze Tier implementation provides the foundational layer for your Personal AI Employee:

- **Obsidian Vault**: Local Markdown-based dashboard and memory
- **File System Watcher**: Monitors a drop folder for new files
- **Qwen Code Integration**: Reasoning engine for processing tasks
- **Human-in-the-Loop**: Approval-based workflow for sensitive actions

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Drop Folder    │────▶│  File Watcher    │────▶│  Needs_Action/  │
│  (files to      │     │  (Python script) │     │  (vault folder) │
│   process)      │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Done/          │◀────│  Qwen Code       │◀────│  Plan/          │
│  (completed)    │     │  (reasoning)     │     │  (action plan)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.13+ | Watcher scripts |
| Qwen Code | Latest | Reasoning engine |
| Obsidian | v1.10.6+ | Dashboard/GUI |

## Installation

### Step 1: Install Python Dependencies

```bash
cd AI_Employee_Vault/scripts
pip install -r requirements.txt
```

### Step 2: Verify Qwen Code

```bash
qwen --version
```

### Step 3: Open Vault in Obsidian

1. Open Obsidian
2. Click "Open folder as vault"
3. Select the `AI_Employee_Vault` folder

## Usage

### Start the File System Watcher

The watcher monitors a drop folder for new files:

```bash
cd AI_Employee_Vault/scripts

# Start watcher (replace paths with your actual paths)
python filesystem_watcher.py "../" "../DropFolder"
```

Or create a DropFolder anywhere and monitor it:

```bash
# Create a drop folder
mkdir C:\DropFolder

# Start watcher
python filesystem_watcher.py "C:\GIAIC Disk\Q4-Nov-2025\Hackathon-q4\Personal_AI_Employee_FTEs\AI_Employee_Vault" "C:\DropFolder"
```

### Process Files

1. **Drop a file** into the monitored folder
2. **Watcher creates** an action file in `Needs_Action/`
3. **Run orchestrator** to process:
   ```bash
   python orchestrator.py "C:\GIAIC Disk\Q4-Nov-2025\Hackathon-q4\Personal_AI_Employee_FTEs\AI_Employee_Vault"
   ```

### Use Qwen Code

Open Qwen Code pointed at the vault:

```bash
cd "C:\GIAIC Disk\Q4-Nov-2025\Hackathon-q4\Personal_AI_Employee_FTEs\AI_Employee_Vault"
qwen
```

Then prompt Qwen to:
- "Check the Needs_Action folder and process any pending items"
- "Review the plan files and suggest next actions"
- "Update the Dashboard with current status"

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md           # Real-time status dashboard
├── Company_Handbook.md    # Rules of engagement
├── Business_Goals.md      # Objectives and metrics
├── Inbox/                 # Raw incoming items
├── Needs_Action/          # Items requiring processing
├── Plans/                 # Action plans
├── Pending_Approval/      # Awaiting human approval
├── Approved/              # Approved actions
├── Rejected/              # Rejected items
├── Done/                  # Completed tasks
├── Logs/                  # System logs
├── Accounting/            # Financial records
├── Invoices/              # Generated invoices
└── scripts/               # Python scripts
    ├── base_watcher.py
    ├── filesystem_watcher.py
    ├── orchestrator.py
    └── requirements.txt
```

## Workflow Example

### 1. Drop a File

Create a text file in the DropFolder:

```
C:\DropFolder\client_request.txt
```

Content:
```
Please send an invoice for the consulting work completed last week.
Amount: $1,500
Client: ABC Corp
```

### 2. Watcher Detects

The File System Watcher creates:
```
AI_Employee_Vault/Needs_Action/FILE_<hash>_client_request.txt.md
```

### 3. Qwen Processes

Run Qwen Code:
```bash
qwen --cwd "AI_Employee_Vault"
```

Prompt:
```
Check the Needs_Action folder and process any pending items.
Create a plan for each item and suggest actions.
```

### 4. Complete Task

After Qwen creates the invoice and logs actions:
- Move item file to `Done/`
- Move plan file to `Done/`
- Dashboard updates automatically

## Configuration

### Company Handbook

Edit `Company_Handbook.md` to customize:
- Communication rules
- Payment thresholds
- Priority levels
- Red flags for escalation

### Business Goals

Edit `Business_Goals.md` to set:
- Revenue targets
- Key metrics
- Active projects
- Subscription tracking

## Troubleshooting

### Watcher doesn't detect files

1. Ensure the DropFolder path is correct
2. Check logs in `Logs/` folder
3. Verify file isn't hidden or temporary

### Qwen Code not reading files

1. Ensure you're in the vault directory
2. Check file permissions
3. Verify `.md` extension on action files

### Dashboard not updating

1. Check that Dashboard.md exists
2. Verify write permissions
3. Check logs for errors

## Next Steps (Silver Tier)

After mastering Bronze tier, consider adding:
- Gmail Watcher for email monitoring
- WhatsApp Watcher for message monitoring
- MCP servers for external actions
- Scheduled tasks (cron/Task Scheduler)
- Human-in-the-loop approval workflow

## Security Notes

- ⚠️ **Never** store credentials in vault files
- ✅ Use environment variables for API keys
- ✅ Keep `.env` files out of version control
- ✅ Review all actions in Logs folder
- ✅ Set appropriate approval thresholds

## License

This is a hackathon project for educational purposes.

---

*Built with ❤️ for the Personal AI Employee Hackathon 2026*
