---
name: approval-workflow
description: |
  Human-in-the-loop approval workflow for sensitive actions. Creates approval
  request files in /Pending_Approval, monitors /Approved folder, and executes
  actions only after human approval. Use for payments, email sends, and other
  sensitive operations.
---

# Approval Workflow Skill

Human-in-the-loop approval system for sensitive actions.

## Overview

This skill implements a file-based approval workflow:

1. **Qwen Code** creates approval request in `/Pending_Approval/`
2. **Human** reviews and moves file to `/Approved/`
3. **Orchestrator** detects approval and executes action
4. **Result** logged and files moved to `/Done/`

## Folder Structure

```
Vault/
├── Pending_Approval/    # Awaiting human review
├── Approved/            # Approved, ready for execution
├── Rejected/            # Rejected actions
└── Done/                # Completed actions
```

## Usage

### Step 1: Create Approval Request

When Qwen Code identifies a sensitive action, it creates:

```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: Invoice #1234
amount: 1500.00
created: 2026-01-07T10:30:00Z
expires: 2026-01-08T10:30:00Z
status: pending
---

# Approval Request: Send Email

## Action Details
- **Type:** Send Email
- **To:** client@example.com
- **Subject:** Invoice #1234
- **Amount:** $1,500.00

## Content
Please find attached invoice #1234 for consulting services.

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

### Step 2: Human Review

Human reviews the file in `/Pending_Approval/` and:
- **Approves**: Move file to `/Approved/`
- **Rejects**: Move file to `/Rejected/`

### Step 3: Automatic Execution

Orchestrator monitors `/Approved/` folder:

```bash
python approval_executor.py "C:/Vault"
```

## Approval Thresholds

Configure in `Company_Handbook.md`:

| Action Type | Auto-Approve | Require Approval |
|-------------|--------------|------------------|
| Email send | Known contacts | New contacts, bulk |
| Payments | < $50 recurring | All new, > $100 |
| Social posts | Scheduled | Replies, DMs |
| File delete | Never | Always |

## Python API

### Create Approval Request

```python
from approval_workflow import ApprovalWorkflow

workflow = ApprovalWorkflow(vault_path="C:/Vault")

# Create approval request
request_id = workflow.create_request(
    action_type="send_email",
    details={
        "to": "client@example.com",
        "subject": "Invoice #1234",
        "body": "Please find attached..."
    },
    priority="normal",
    expires_in_hours=24
)

print(f"Created approval request: {request_id}")
```

### Check Approval Status

```python
status = workflow.check_status(request_id)
print(f"Status: {status}")  # pending, approved, rejected, expired
```

### Execute Approved Actions

```python
# Monitor and execute approved actions
workflow.execute_approved_actions()
```

## Command Line

### Create Approval Request

```bash
python approval_workflow.py create \
  --vault "C:/Vault" \
  --action "send_email" \
  --to "client@example.com" \
  --subject "Invoice #1234" \
  --body "Please find attached..."
```

### Check Pending Requests

```bash
python approval_workflow.py list --vault "C:/Vault"
```

### Execute Approved Actions

```bash
python approval_workflow.py execute --vault "C:/Vault"
```

## Approval Request Schema

```json
{
  "type": "approval_request",
  "action": "send_email|payment|post|delete|custom",
  "created": "2026-01-07T10:30:00Z",
  "expires": "2026-01-08T10:30:00Z",
  "status": "pending|approved|rejected|expired",
  "priority": "low|normal|high|critical",
  "details": {
    "to": "client@example.com",
    "subject": "Invoice #1234"
  },
  "metadata": {
    "source": "gmail_watcher",
    "original_id": "EMAIL_12345"
  }
}
```

## Expiration Handling

Expired approvals are automatically:
1. Moved to `/Rejected/`
2. Logged with reason "expired"
3. Original task flagged for review

## Logging

All approval actions logged to:
```
Vault/Logs/approvals/YYYY-MM-DD.log
```

Log entry:
```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "request_id": "APR_12345",
  "action": "send_email",
  "status": "approved",
  "approved_by": "human",
  "executed_at": "2026-01-07T10:35:00Z",
  "result": "success"
}
```

## Examples

### Email Approval

```bash
python approval_workflow.py create \
  --vault "C:/Vault" \
  --action "send_email" \
  --to "billing@client.com" \
  --subject "Invoice #2026-001" \
  --body "Payment due within 30 days" \
  --attachment "Vault/Invoices/2026-001.pdf"
```

### Payment Approval

```bash
python approval_workflow.py create \
  --vault "C:/Vault" \
  --action "payment" \
  --recipient "Vendor Inc" \
  --amount "500.00" \
  --reason "Invoice #V-123 payment" \
  --priority "high"
```

### Social Media Post Approval

```bash
python approval_workflow.py create \
  --vault "C:/Vault" \
  --action "social_post" \
  --platform "linkedin" \
  --content "Excited to announce our new product..." \
  --schedule "2026-01-08T09:00:00Z"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| File not detected | Ensure file moved to /Approved (not copied) |
| Action not executing | Check orchestrator is running |
| Expired too soon | Increase expires_in_hours |
| Wrong threshold | Update Company_Handbook.md rules |

## Security Notes

- ⚠️ Never auto-approve payments to new recipients
- ⚠️ Always require approval for > $500 transactions
- ✅ Log all approval decisions
- ✅ Set reasonable expiration times
- ✅ Review rejected items weekly
