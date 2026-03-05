---
name: plan-creator
description: |
  Create structured action plans from tasks in Needs_Action folder. Analyzes
  incoming items, breaks them into actionable steps, identifies required
  approvals, and generates Plan.md files for Qwen Code to execute.
---

# Plan Creator Skill

Generate structured action plans for tasks.

## Overview

This skill analyzes tasks and creates detailed plans:
1. Read item from `/Needs_Action/`
2. Analyze content and context
3. Break into actionable steps
4. Identify approval requirements
5. Generate `Plan.md` in `/Plans/`

## Usage

### Automatic (via Orchestrator)

The orchestrator automatically calls plan-creator when new items arrive:

```bash
python orchestrator.py "C:/Vault"
```

### Manual

```bash
python plan_creator.py "C:/Vault" --item "EMAIL_12345.md"
```

### From Qwen Code

```
Create a plan for the pending items in Needs_Action folder.
Use the plan-creator skill to generate structured plans.
```

## Plan Structure

Generated plans follow this format:

```markdown
---
created: 2026-01-07T10:30:00Z
source: EMAIL_12345_client_request.md
status: in_progress
priority: normal
estimated_steps: 5
requires_approval: true
---

# Plan: Send Invoice to Client

## Objective
Generate and send invoice for consulting services.

## Context
- **Source:** Email from client requesting invoice
- **Client:** ABC Corp
- **Amount:** $1,500
- **Due:** Net 30

## Steps
- [ ] Review client email and extract details
- [ ] Check Company_Handbook.md for invoice rules
- [ ] Generate invoice PDF
- [ ] Create approval request (amount > $500)
- [ ] Wait for human approval
- [ ] Send email with invoice attached
- [ ] Log transaction in Accounting/
- [ ] Move to Done when complete

## Approval Required
| Action | Threshold | Status |
|--------|-----------|--------|
| Send Email | Amount > $500 | Pending |

## Resources
- Company_Handbook.md: Invoice rules
- Business_Goals.md: Client rates
- Templates/invoice_template.md

## Notes
_Add notes during execution_
```

## Python API

```python
from plan_creator import PlanCreator

creator = PlanCreator(vault_path="C:/Vault")

# Create plan from item
plan = creator.create_plan(
    item_path="Needs_Action/EMAIL_12345.md"
)

print(f"Created plan: {plan['id']}")
print(f"Steps: {plan['step_count']}")
print(f"Requires approval: {plan['requires_approval']}")

# Update plan status
creator.update_status(plan['id'], 'completed')
```

## Command Line

### Create Plan

```bash
python plan_creator.py create \
  --vault "C:/Vault" \
  --item "Needs_Action/EMAIL_12345.md"
```

### List Plans

```bash
python plan_creator.py list --vault "C:/Vault"
```

### Get Plan Status

```bash
python plan_creator.py status \
  --vault "C:/Vault" \
  --plan "PLAN_12345.md"
```

## Plan Templates

### Email Response Plan

```yaml
template: email_response
steps:
  - Read email and understand request
  - Check Company_Handbook.md for response rules
  - Draft response
  - Create approval request if needed
  - Send email
  - Log action
```

### Invoice Generation Plan

```yaml
template: invoice
steps:
  - Extract client details
  - Calculate amount from rates
  - Generate invoice PDF
  - Create approval request
  - Send via email
  - Log in Accounting/
```

### Task Processing Plan

```yaml
template: task
steps:
  - Understand task requirements
  - Identify required resources
  - Break into sub-tasks
  - Execute each sub-task
  - Verify completion
  - Log and move to Done
```

## Approval Detection

The plan-creator automatically detects when approval is needed:

| Action | Threshold | Check |
|--------|-----------|-------|
| Email send | New recipient | Company_Handbook.md |
| Payment | > $100 | Company_Handbook.md |
| Payment | New payee | Always |
| File delete | Any | Always |
| Social post | Reply/DM | Always |

## Integration with Approval Workflow

Plans that require approval automatically create approval requests:

```python
# In plan_creator.py
if requires_approval:
    approval_id = workflow.create_request(
        action_type=action,
        details=action_details,
        priority=priority
    )
    plan['approval_request'] = approval_id
```

## Logging

All plan creations logged to:
```
Vault/Logs/plans/YYYY-MM-DD.log
```

Log entry:
```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "plan_id": "PLAN_12345",
  "source": "EMAIL_12345.md",
  "steps": 5,
  "requires_approval": true,
  "status": "created"
}
```

## Examples

### Simple Email Response

Input:
```
From: client@example.com
Subject: Quick question
Body: What are your rates?
```

Generated Plan:
```markdown
## Steps
- [ ] Read email
- [ ] Check rates in Business_Goals.md
- [ ] Draft response with rates
- [ ] Send email (no approval needed - known contact)
- [ ] Log action
```

### Invoice Request (Requires Approval)

Input:
```
From: billing@client.com
Subject: Invoice needed
Body: Please send invoice for $2,000
```

Generated Plan:
```markdown
## Steps
- [ ] Extract invoice details
- [ ] Generate invoice PDF
- [ ] Create approval request (amount > $500)
- [ ] Wait for approval
- [ ] Send email with attachment
- [ ] Log in Accounting/
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Plan not created | Check item exists in Needs_Action |
| Wrong steps | Update plan template |
| Approval not detected | Check Company_Handbook thresholds |
| Plan stuck | Manually update status |

## Best Practices

1. **Be specific**: Clear, actionable steps
2. **Include context**: Link to source item
3. **Track approvals**: Note what's needed
4. **Log everything**: Update status as you go
5. **Reference docs**: Link to relevant handbook sections
