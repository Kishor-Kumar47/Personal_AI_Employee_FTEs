---
name: linkedin-poster
description: |
  Post updates to LinkedIn automatically. Create business posts, share updates,
  and generate engagement. Supports text posts, images, and scheduled posting.
  Requires LinkedIn authentication via Playwright browser automation.
---

# LinkedIn Poster Skill

Automatically post updates to LinkedIn for business promotion.

## Overview

This skill uses Playwright browser automation to:
- Post text updates to LinkedIn
- Post images with captions
- Schedule posts for optimal times
- Track engagement (likes, comments)

## Prerequisites

```bash
# Install Playwright
pip install playwright
playwright install

# Login to LinkedIn once to save session
python linkedin_poster.py --login
```

## Usage

### Post Text Update

```bash
python linkedin_poster.py post \
  --content "Excited to announce our new AI Employee product! 
             Automate your business with intelligent agents. 
             #AI #Automation #Innovation"
```

### Post with Image

```bash
python linkedin_poster.py post \
  --content "Check out our latest project milestone!" \
  --image "C:/Vault/Images/milestone.png"
```

### Schedule Post

```bash
python linkedin_poster.py schedule \
  --content "Monday motivation: Automate the boring stuff!" \
  --time "2026-01-13T09:00:00"
```

### Generate Business Post

```bash
python linkedin_poster.py generate \
  --topic "product_launch" \
  --details "New AI Employee Silver Tier released"
```

## Python API

```python
from linkedin_poster import LinkedInPoster

poster = LinkedInPoster(session_path="./session")

# Post text
poster.post("Excited to share our latest achievement! #milestone")

# Post with image
poster.post_with_image(
    content="Check out our new office!",
    image_path="office.jpg"
)

# Schedule post
poster.schedule_post(
    content="Monday motivation!",
    scheduled_time="2026-01-13T09:00:00"
)

# Generate post from topic
content = poster.generate_post(
    topic="business_update",
    details={
        "revenue": "$10,000 MTD",
        "clients": "15 active clients"
    }
)
```

## Post Templates

### Business Update

```
📊 Business Update

This week's highlights:
• Revenue: {revenue}
• New clients: {new_clients}
• Projects completed: {completed}

Grateful for our amazing clients! 🙏

#Business #Growth #Success
```

### Product Announcement

```
🚀 Exciting News!

We're thrilled to announce {product_name}!

Key features:
• {feature_1}
• {feature_2}
• {feature_3}

Learn more: {link}

#Innovation #Product #Launch
```

### Thought Leadership

```
💡 Industry Insight

{insight_content}

Key takeaways:
1. {takeaway_1}
2. {takeaway_2}
3. {takeaway_3}

What's your experience? Share below! 👇

#Leadership #Industry #Insights
```

## Content Guidelines

### Best Practices

1. **Length**: 100-300 characters for optimal engagement
2. **Hashtags**: 3-5 relevant hashtags
3. **Timing**: Post between 9-11 AM on weekdays
4. **Frequency**: 1-2 posts per day maximum
5. **Engagement**: Respond to comments within 24 hours

### Content Rules

| Content Type | Approval Required |
|--------------|-------------------|
| Business updates | No (auto-approve) |
| Product announcements | Yes |
| Responses to comments | Yes |
| Promotional content | Yes |

## Scheduling

### Best Times to Post

- **Tuesday-Thursday**: 9-11 AM (highest engagement)
- **Monday/Friday**: 12-1 PM
- **Weekend**: Avoid (low professional engagement)

### Schedule Commands

```bash
# Schedule for tomorrow 9 AM
python linkedin_poster.py schedule \
  --content "Tomorrow's post" \
  --time "2026-01-08T09:00:00"

# List scheduled posts
python linkedin_poster.py list-scheduled

# Cancel scheduled post
python linkedin_poster.py cancel --id "SCHED_12345"
```

## Approval Workflow

For sensitive posts, create approval request:

```bash
python approval_workflow.py create \
  --vault "C:/Vault" \
  --action "linkedin_post" \
  --content "Product launch announcement..." \
  --priority "normal"
```

## Logging

All posts logged to:
```
Vault/Logs/linkedin/YYYY-MM-DD.log
```

Log entry:
```json
{
  "timestamp": "2026-01-07T10:00:00Z",
  "action": "post",
  "content": "Post content...",
  "status": "success",
  "post_url": "https://linkedin.com/posts/..."
}
```

## Examples

### Daily Business Update

```bash
python linkedin_poster.py post \
  --template "business_update" \
  --data '{"revenue": "$5,000", "new_clients": "2", "completed": "3"}'
```

### Client Success Story

```bash
python linkedin_poster.py post \
  --content "🎉 Client Success Story!
  
  Helped ABC Corp reduce processing time by 80% 
  with our AI Employee solution.
  
  Results:
  • 80% faster processing
  • 50% cost reduction
  • 100% accuracy
  
  Ready to transform your business? Let's talk!
  
  #ClientSuccess #AI #Automation"
```

### Industry Insight

```bash
python linkedin_poster.py generate \
  --topic "industry_insight" \
  --details '{"trend": "AI automation", "stat": "60% of businesses adopting AI"}'
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Not logged in | Run `python linkedin_poster.py --login` |
| Post failed | Check session cookies, re-login |
| Image upload fails | Verify image path and format |
| Rate limited | Wait 24 hours, reduce posting frequency |

## Security Notes

- ⚠️ Never post sensitive business information
- ✅ Review all posts before publishing
- ✅ Use approval workflow for important announcements
- ✅ Keep session cookies secure
