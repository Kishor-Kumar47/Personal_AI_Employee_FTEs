# Silver Tier MCP Server Setup Guide

## ✅ What's Configured

| MCP Server | Status | Purpose |
|------------|--------|---------|
| **filesystem** | ✅ Installed | Read/write files in vault |
| **email-sender** | ✅ Configured | Send emails via Gmail API |

---

## 📁 Folder Structure Setup

Run these commands to create required folders:

```bash
cd "C:\GIAIC Disk\Q4-Nov-2025\Hackathon-q4\Personal_AI_Employee_FTEs\AI_Employee_Vault"

# Create Silver Tier folders
mkdir Pending_Approval Approved Rejected In_Progress Plans Briefings Accounting
```

---

## 🔧 MCP Server Configuration

### Config Location
```
C:\Users\DELL\AppData\Roaming\claude-code\mcp.json
```

### Current Configuration
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\GIAIC Disk\\Q4-Nov-2025\\Hackathon-q4\\Personal_AI_Employee_FTEs\\AI_Employee_Vault"]
    },
    "email-sender": {
      "command": "python",
      "args": ["C:\\GIAIC Disk\\Q4-Nov-2025\\Hackathon-q4\\Personal_AI_Employee_FTEs\\.qwen\\skills\\email-sender\\send_email.py"]
    }
  }
}
```

---

## 📧 Email Sender Setup

### Option 1: Gmail API (Recommended - Already Configured)

Your Gmail API credentials are already set up:
- `credentials.json` → Project root
- `token.json` → `AI_Employee_Vault/scripts/`

**Test email sending:**
```bash
cd "C:\GIAIC Disk\Q4-Nov-2025\Hackathon-q4\Personal_AI_Employee_FTEs\.qwen\skills\email-sender"

# Dry run test (won't actually send)
set DRY_RUN=true
python send_email.py --to "test@example.com" --subject "Test" --body "Hello"
```

### Option 2: SMTP (Alternative)

Set environment variables:
```bash
# Create .env file in project root
echo EMAIL_ADDRESS=your-email@gmail.com > .env
echo EMAIL_PASSWORD=your-app-password >> .env
echo EMAIL_SMTP_SERVER=smtp.gmail.com >> .env
echo EMAIL_SMTP_PORT=587 >> .env
```

**Get Gmail App Password:**
1. Go to: https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to: https://myaccount.google.com/apppasswords
4. Create app password for "Mail"
5. Use this password in `.env`

---

## 📱 WhatsApp Setup (Optional for Silver)

### WhatsApp Web Automation (Unofficial)

**Step 1: Install Playwright**
```bash
pip install playwright
playwright install chromium
```

**Step 2: Create WhatsApp Watcher**

The watcher script already exists in your project. To use it:

```bash
cd "C:\GIAIC Disk\Q4-Nov-2025\Hackathon-q4\Personal_AI_Employee_FTEs\AI_Employee_Vault\scripts"

# Run WhatsApp watcher (will open browser for QR scan)
python whatsapp_watcher.py "../" --once
```

**⚠️ Warning:** WhatsApp Web automation may violate ToS. Use at your own risk.

### WhatsApp Business API (Official - Recommended for Production)

**Step 1: Create Meta Developer Account**
1. Visit: https://developers.facebook.com/
2. Create account
3. Create new app → Business → WhatsApp

**Step 2: Get Credentials**
- Phone Number ID
- Business Account ID  
- Access Token

**Step 3: Store Credentials**
```bash
# Add to .env file (NEVER commit to git)
WHATSAPP_PHONE_ID=your-phone-id
WHATSAPP_BUSINESS_ID=your-business-id
WHATSAPP_ACCESS_TOKEN=your-access-token
```

---

## 🏥 Odoo ERP Setup (Gold Tier)

### Option 1: Local Installation (Free)

**Step 1: Download Odoo Community**
1. Visit: https://www.odoo.com/page/download
2. Select: **Community Edition** → **Windows**
3. Download installer (~200MB)

**Step 2: Install**
```
# Run installer
- Install path: C:\Odoo19
- Port: 8069 (default)
- Database: PostgreSQL (included)
```

**Step 3: Access Odoo**
1. Open browser: http://localhost:8069
2. Create database:
   - Name: `ai_employee_db`
   - Email: your-email@gmail.com
   - Password: create-master-password

**Step 4: Enable API Access**
1. Go to: Settings → Users → Your User
2. Enable **API Access**
3. Generate API Key
4. Note credentials:
   - URL: `http://localhost:8069`
   - Database: `ai_employee_db`
   - Username: your-email@gmail.com
   - API Key: (generated)

**Step 5: Odoo MCP Server**
```bash
# Install Odoo MCP
npm install -g @alanogic/mcp-odoo-adv

# Or use official Odoo JSON-RPC
# Docs: https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
```

**Step 6: Add to MCP Config**
```json
{
  "mcpServers": {
    "odoo": {
      "command": "npx",
      "args": ["-y", "@alanogic/mcp-odoo-adv"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "ai_employee_db",
        "ODOO_USERNAME": "your-email@gmail.com",
        "ODOO_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Option 2: Odoo Online (SaaS - Easier)

**Step 1: Sign Up**
1. Visit: https://www.odoo.com/trial
2. Select free plan
3. Choose apps: Accounting, Invoicing, CRM

**Step 2: Get API Key**
1. Settings → Users → Your Profile
2. Generate API Key

**⚠️ Note:** Odoo Online has limited API access. Self-hosted gives full control.

---

## 🧪 Testing MCP Servers

### Test Filesystem MCP
```bash
# Start Claude Code
claude

# In Claude, try:
@filesystem List files in AI_Employee_Vault/Needs_Action
```

### Test Email MCP
```bash
# Dry run test
set DRY_RUN=true
python .qwen\skills\email-sender\send_email.py --to "test@example.com" --subject "MCP Test" --body "Testing MCP email"
```

---

## ✅ Silver Tier Checklist

| Requirement | Status | Command to Verify |
|-------------|--------|-------------------|
| Gmail Watcher | ✅ Complete | `python gmail_watcher.py <vault> --once` |
| 2+ Watchers | ⚠️ Partial | Need LinkedIn working |
| MCP Server | ✅ Configured | Check `mcp.json` |
| Approval Workflow | ⏳ Setup needed | Create folders |
| Plan Creation | ⏳ Not tested | Use plan-creator skill |
| Scheduler | ⏳ Not configured | Windows Task Scheduler |

---

## 🚀 Next Steps

1. **Create Approval Folders:**
   ```bash
   cd "AI_Employee_Vault"
   mkdir Pending_Approval Approved Rejected
   ```

2. **Test MCP in Claude:**
   ```bash
   claude
   # Ask: "List files in Needs_Action folder"
   ```

3. **Test Email Sending:**
   ```bash
   set DRY_RUN=true
   python .qwen\skills\email-sender\send_email.py --to "your-email@gmail.com" --subject "Test" --body "MCP Test"
   ```

4. **Run LinkedIn Watcher:**
   ```bash
   python linkedin_watcher.py "../" --once
   ```

5. **Set up Windows Task Scheduler** (see scheduler skill)

---

## 📝 Environment Variables (.env file)

Create `.env` in project root:
```bash
# Email (for SMTP)
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587

# Dry Run Mode (set to false for production)
DRY_RUN=true

# WhatsApp (optional)
WHATSAPP_PHONE_ID=
WHATSAPP_BUSINESS_ID=
WHATSAPP_ACCESS_TOKEN=

# Odoo (Gold tier - optional)
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_db
ODOO_USERNAME=your-email@gmail.com
ODOO_API_KEY=your-api-key
```

**⚠️ IMPORTANT:** `.env` is in `.gitignore` - never commit secrets!
