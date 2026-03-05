---
name: email-sender
description: |
  Send emails via SMTP or Gmail API. Use for sending invoices, replies, notifications,
  and business communications. Supports attachments, HTML content, and CC/BCC.
  Requires email credentials configured in environment variables.
---

# Email Sender Skill

Send emails programmatically via SMTP or Gmail API.

## Prerequisites

### Option 1: Gmail API (Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json`
6. Run the authorization script once to generate `token.json`

### Option 2: SMTP

Set environment variables:
```bash
export EMAIL_SMTP_SERVER="smtp.gmail.com"
export EMAIL_SMTP_PORT="587"
export EMAIL_ADDRESS="your@email.com"
export EMAIL_PASSWORD="your-app-password"
```

## Setup

### Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Gmail API Authorization (First Time Only)

```bash
cd .qwen/skills/email-sender
python authorize_gmail.py
```

## Usage

### Send Simple Email

```bash
python send_email.py \
  --to "recipient@example.com" \
  --subject "Invoice #1234" \
  --body "Please find attached your invoice for January 2026."
```

### Send Email with Attachment

```bash
python send_email.py \
  --to "client@company.com" \
  --subject "Invoice #1234" \
  --body "Please find attached your invoice." \
  --attachment "C:/Vault/Invoices/invoice_1234.pdf"
```

### Send Email with CC

```bash
python send_email.py \
  --to "client@company.com" \
  --cc "manager@company.com" \
  --subject "Project Update" \
  --body "Here's the weekly progress report."
```

### Send HTML Email

```bash
python send_email.py \
  --to "client@company.com" \
  --subject "Monthly Report" \
  --html-body "<h1>Monthly Report</h1><p>Revenue: $10,000</p>"
```

## Python API

```python
from email_sender import EmailSender

sender = EmailSender()

# Send simple email
sender.send(
    to="client@example.com",
    subject="Hello",
    body="This is a test email"
)

# Send with attachment
sender.send(
    to="client@example.com",
    subject="Invoice",
    body="Please find attached",
    attachments=["/path/to/invoice.pdf"]
)

# Send with CC/BCC
sender.send(
    to="client@example.com",
    cc="manager@example.com",
    bcc="archive@example.com",
    subject="Report",
    body="Quarterly results"
)
```

## Dry Run Mode

Test without actually sending:

```bash
export DRY_RUN=true
python send_email.py --to "test@example.com" --subject "Test" --body "Dry run"
```

Output:
```
[DRY RUN] Would send email to test@example.com
[DRY RUN] Subject: Test
[DRY RUN] Body: Dry run
```

## Templates

### Invoice Email

```bash
python send_email.py \
  --to "client@company.com" \
  --subject "Invoice #{{invoice_number}}" \
  --template "invoice" \
  --data '{"invoice_number": "1234", "amount": "$1,500", "due_date": "2026-02-15"}'
```

### Follow-up Email

```bash
python send_email.py \
  --to "prospect@company.com" \
  --subject "Following up on our conversation" \
  --template "followup" \
  --data '{"contact_name": "John", "product": "Consulting Services"}'
```

## Response Format

Success:
```json
{
  "status": "success",
  "message_id": "<abc123@mail.gmail.com>",
  "to": "recipient@example.com",
  "subject": "Invoice #1234",
  "sent_at": "2026-01-07T10:30:00Z"
}
```

Error:
```json
{
  "status": "error",
  "error": "Authentication failed",
  "details": "Invalid credentials"
}
```

## Logging

All sent emails are logged to:
```
Vault/Logs/emails/YYYY-MM-DD.log
```

Log entry format:
```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "to": "client@example.com",
  "subject": "Invoice #1234",
  "status": "sent",
  "message_id": "<abc123@mail.gmail.com>"
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Re-run authorize_gmail.py |
| token.json not found | Run authorization first |
| Attachment not found | Check file path is absolute |
| Rate limited | Wait 1 hour, reduce send frequency |
| Gmail API quota exceeded | Check Google Cloud Console quotas |

## Security Notes

- ⚠️ Never commit `token.json` or `credentials.json`
- ✅ Add to `.gitignore`
- ✅ Use app-specific passwords for SMTP
- ✅ Enable 2FA on email account
- ✅ Review sent emails in Logs folder

## Rate Limits

| Account Type | Daily Limit | Per Minute |
|--------------|-------------|------------|
| Gmail Free | 500 emails | 60 emails |
| Gmail Workspace | 2,000 emails | 60 emails |
| SMTP | Varies by provider | Varies |

## Examples

### Send Invoice

```bash
python send_email.py \
  --to "billing@client.com" \
  --subject "Invoice #2026-001 - $1,500" \
  --body "Dear Client, Please find attached invoice #2026-001 for consulting services. Payment due within 30 days." \
  --attachment "Vault/Invoices/2026-001.pdf"
```

### Send Meeting Confirmation

```bash
python send_email.py \
  --to "meeting@example.com" \
  --subject "Meeting Confirmation - Tomorrow 2PM" \
  --body "Hi, This is a confirmation for our meeting tomorrow at 2PM. Looking forward to speaking with you."
```

### Send Bulk Notification (with rate limiting)

```bash
python send_bulk.py \
  --recipients "list.csv" \
  --subject "Product Update" \
  --template "update" \
  --rate-limit 10  # 10 emails per minute
```
