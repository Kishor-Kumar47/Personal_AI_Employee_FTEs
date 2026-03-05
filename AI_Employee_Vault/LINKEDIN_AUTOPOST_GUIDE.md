# Automatic LinkedIn Posting Guide

## Quick Start

### Option 1: One-Time Post (Recommended)

```bash
cd C:\GIAIC Disk\Q4-Nov-2025\Hackathon-q4\Personal_AI_Employee_FTEs\AI_Employee_Vault\scripts

python linkedin_auto_post.py --email "your@email.com" --password "your_password" --content "Your post content here #AI #Automation"
```

### Option 2: Save Credentials (Easier)

1. **Create `.env` file** in project root:
   ```bash
   cd C:\GIAIC Disk\Q4-Nov-2025\Hackathon-q4\Personal_AI_Employee_FTEs
   copy .env.example .env
   ```

2. **Edit `.env`** with your credentials:
   ```
   LINKEDIN_EMAIL=your@email.com
   LINKEDIN_PASSWORD=your_password
   ```

3. **Post without typing credentials:**
   ```bash
   cd AI_Employee_Vault/scripts
   python linkedin_auto_post.py --content "Your post content #AI"
   ```

## Examples

### Simple Text Post
```bash
python linkedin_auto_post.py --content "Excited to announce our AI Employee project! Automating business workflows with Qwen Code. #AI #Automation #Innovation"
```

### Post with Image
```bash
python linkedin_auto_post.py --content "Check out our latest milestone!" --image "C:\path\to\image.png"
```

### Using Environment Variables
```bash
set LINKEDIN_EMAIL=your@email.com
set LINKEDIN_PASSWORD=your_password
python linkedin_auto_post.py --content "Your post here"
```

## Automated Workflow with Qwen Code

### Step 1: Ask Qwen to Create Post Content

```bash
cd C:\GIAIC Disk\Q4-Nov-2025\Hackathon-q4\Personal_AI_Employee_FTEs\AI_Employee_Vault
qwen
```

Prompt:
```
Create 3 LinkedIn post options about our AI Employee Silver Tier project.
Include:
- What we built (Gmail Watcher, LinkedIn integration, automated plans)
- Key achievements
- Relevant hashtags
Keep each under 300 characters.
```

### Step 2: Copy the Best Post

```bash
cd scripts
python linkedin_auto_post.py --content "🚀 AI Employee Silver Tier Complete!

✅ Gmail Watcher - Auto-fetches emails
✅ LinkedIn Integration - Email notifications  
✅ Auto-posting to LinkedIn
✅ Qwen Code reasoning loop
✅ Human-in-the-loop approvals

Built with Python + Playwright + Qwen Code.

#AI #Automation #LinkedIn #Python #QwenCode"
```

## Scheduling Posts

### Windows Task Scheduler

```bash
python scheduler.py create ^
  --vault "../" ^
  --name "LinkedIn_Daily_Post" ^
  --command "python" ^
  --args "AI_Employee_Vault/scripts/linkedin_auto_post.py --content \"Daily business update #AI\"" ^
  --schedule "daily" ^
  --time "09:00"
```

### Manual Schedule File

Create `scheduled_posts.json`:
```json
{
  "posts": [
    {
      "time": "2026-03-03T09:00:00",
      "content": "Monday motivation post...",
      "hashtags": ["#Monday", "#Motivation"]
    }
  ]
}
```

## Post Templates

### Business Update
```
📊 Business Update

This week we achieved:
• [Achievement 1]
• [Achievement 2]
• [Achievement 3]

Grateful for the progress! 🙏

#Business #Growth #AI
```

### Product Announcement
```
🚀 Exciting News!

We just launched [Product/Feature]!

Key benefits:
• [Benefit 1]
• [Benefit 2]
• [Benefit 3]

Learn more: [Link]

#Innovation #Product #Launch
```

### Thought Leadership
```
💡 Industry Insight

[Your insight about AI/automation]

Key takeaways:
1. [Takeaway 1]
2. [Takeaway 2]
3. [Takeaway 3]

What's your experience? Share below! 👇

#Leadership #AI #Insights
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login failed | Check email/password, try manual login first |
| Post not publishing | Wait for page to load, check network |
| Browser closes too fast | Script takes screenshot for verification |
| "Post may have been published" | Check your LinkedIn feed manually |

## Security Notes

⚠️ **Important:**
- Never commit `.env` file to git (add to `.gitignore`)
- Use a dedicated app password if possible
- Monitor LinkedIn for unusual activity
- Don't post too frequently (LinkedIn may flag as spam)

## Best Practices

1. **Post Timing:** 9-11 AM on weekdays (best engagement)
2. **Frequency:** 1-2 posts per day maximum
3. **Content:** Mix of business updates, insights, and engagement
4. **Hashtags:** 3-5 relevant hashtags per post
5. **Images:** Posts with images get 2x engagement

## Full Automation (Advanced)

Create a batch file `auto_linkedin.bat`:

```batch
@echo off
cd /d "%~dp0AI_Employee_Vault\scripts"

REM Generate post content with Qwen (optional)
REM qwen -p "Create a LinkedIn post about today's progress"

REM Post to LinkedIn
python linkedin_auto_post.py --content "%~1"

echo Post attempted at %date% %time% >> ../Logs/linkedin_posts.log
```

Usage:
```bash
auto_linkedin.bat "Your post content here #AI"
```

---

*Automatic LinkedIn Posting - AI Employee Silver Tier*
