---
name: ceo-briefing
description: |
  Generate weekly CEO Briefing reports with business audit, revenue tracking,
  bottlenecks analysis, and proactive suggestions. Reads from Business_Goals.md,
  accounting data, and completed tasks to create executive summaries.
---

# CEO Briefing Generator

Generate comprehensive weekly business reports automatically.

## Overview

This skill creates the "Monday Morning CEO Briefing" by analyzing:
- Business goals and metrics
- Completed tasks from the week
- Accounting/financial data
- Email and communication patterns
- Social media engagement

## Usage

### Generate Weekly Briefing

```bash
python ceo_briefing.py --vault "C:/Vault" --period "last_week"
```

### Generate Daily Summary

```bash
python ceo_briefing.py --vault "C:/Vault" --period "yesterday"
```

### Generate Monthly Report

```bash
python ceo_briefing.py --vault "C:/Vault" --period "last_month"
```

## Output

Briefing is saved to `Vault/Briefings/YYYY-MM-DD_Briefing.md`

## Briefing Structure

```markdown
# Monday Morning CEO Briefing

## Executive Summary
Brief overview of the week's performance.

## Revenue
- This Week: $X,XXX
- MTD: $X,XXX (XX% of target)
- Trend: On track / Behind / Ahead

## Completed Tasks
- [x] Task 1
- [x] Task 2

## Bottlenecks
| Task | Expected | Actual | Delay |
|------|----------|--------|-------|
| X    | 2 days   | 5 days | +3 days |

## Proactive Suggestions

### Cost Optimization
- Subscription not used in 30 days
- Duplicate services detected

### Upcoming Deadlines
- Project due dates
- Payment due dates

## Action Items
- [ ] Review subscription costs
- [ ] Follow up on delayed tasks
```

## Python API

```python
from ceo_briefing import CEOBriefing

briefing = CEOBriefing(vault_path="C:/Vault")

# Generate weekly briefing
report = briefing.generate_weekly()

# Get revenue summary
revenue = briefing.get_revenue_summary()

# Find bottlenecks
bottlenecks = briefing.analyze_bottlenecks()

# Generate suggestions
suggestions = briefing.generate_suggestions()
```

## Data Sources

| Source | File/Folder | Purpose |
|--------|-------------|---------|
| Business Goals | Business_Goals.md | Targets and metrics |
| Completed Tasks | Done/ | Task completion analysis |
| Accounting | Accounting/ | Revenue and expenses |
| Emails | Logs/emails/ | Communication volume |
| Social | Logs/linkedin/ | Social media activity |

## Scheduling

### Weekly (Monday 7 AM)

```bash
python scheduler.py create \
  --vault "C:/Vault" \
  --name "Weekly_CEO_Briefing" \
  --command "python" \
  --args "ceo_briefing.py --vault 'C:/Vault' --period last_week" \
  --schedule "weekly" \
  --day "monday" \
  --time "07:00"
```

## Metrics Tracked

| Metric | Calculation | Alert Threshold |
|--------|-------------|-----------------|
| Revenue MTD | Sum of invoices | < 80% of target |
| Task Completion | Done/ this week | < 15 tasks |
| Response Time | Email timestamp diff | > 48 hours |
| Subscription Cost | Sum of subscriptions | > $600/month |

## Examples

### Weekly Briefing Output

```markdown
---
generated: 2026-03-03T07:00:00Z
period: 2026-02-24 to 2026-03-02
---

# Monday Morning CEO Briefing

## Executive Summary
Strong week with revenue ahead of target. Completed 23 tasks.
One bottleneck identified in client proposal process.

## Revenue
- **This Week**: $2,450
- **MTD**: $4,500 (45% of $10,000 target)
- **Trend**: On track

## Completed Tasks
- [x] Client A invoice sent and paid ($1,500)
- [x] Project Alpha milestone delivered
- [x] LinkedIn posts scheduled (5 posts)
- [x] Email responses (18 emails)

## Bottlenecks
| Task | Expected | Actual | Delay |
|------|----------|--------|-------|
| Client B proposal | 2 days | 5 days | +3 days |

## Proactive Suggestions

### Cost Optimization
- **Notion**: No team activity in 45 days. Cost: $15/month.
  - [ACTION] Cancel subscription? Move to /Pending_Approval

### Upcoming Deadlines
- Project Alpha final: March 15 (12 days)
- Quarterly tax prep: March 31 (28 days)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No revenue data | Check Accounting/ folder has invoices |
| Empty briefing | Verify Done/ folder has completed tasks |
| Wrong period | Check date range in command |
