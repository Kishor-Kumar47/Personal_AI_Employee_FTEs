"""
Email Sender - Send emails via SMTP or Gmail API

Usage:
    python send_email.py --to "recipient@example.com" --subject "Hello" --body "Message"
    python send_email.py --to "recipient@example.com" --subject "Hello" --body "Message" --attachment "file.pdf"
"""

import os
import sys
import json
import logging
import argparse
import smtplib
import base64
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Try to import Gmail API libraries
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GMAIL_API_AVAILABLE = True
except ImportError:
    GMAIL_API_AVAILABLE = False


class EmailSender:
    """Send emails via SMTP or Gmail API"""
    
    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path) if vault_path else Path.cwd()
        self.logs_dir = self.vault_path / 'Logs' / 'emails'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration from environment
        self.smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
        self.email_address = os.getenv('EMAIL_ADDRESS', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        
        # Gmail API
        self.gmail_service = None
        self.scopes = ['https://www.googleapis.com/auth/gmail.send']
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def authenticate_gmail(self, credentials_path: str = None, token_path: str = None) -> bool:
        """Authenticate with Gmail API"""
        if not GMAIL_API_AVAILABLE:
            self.logger.error('Gmail API libraries not installed')
            return False
        
        default_credentials = Path(__file__).parent / 'credentials.json'
        default_token = Path(__file__).parent / 'token.json'
        
        credentials_path = Path(credentials_path) if credentials_path else default_credentials
        token_path = Path(token_path) if token_path else default_token
        
        creds = None
        
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(token_path, self.scopes)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not credentials_path.exists():
                    self.logger.error(f'Credentials file not found: {credentials_path}')
                    return False
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.scopes)
                creds = flow.run_local_server(port=0)
                token_path.write_text(creds.to_json())
        
        self.gmail_service = build('gmail', 'v1', credentials=creds)
        return True
    
    def send(self, to: str, subject: str, body: str, 
             cc: str = None, bcc: str = None,
             attachments: list = None, html: bool = False) -> dict:
        """Send an email"""
        if self.dry_run:
            return self._dry_run_send(to, subject, body, cc, attachments)
        
        # Create message
        message = MIMEMultipart()
        message['From'] = self.email_address
        message['To'] = to
        message['Subject'] = subject
        
        if cc:
            message['Cc'] = cc
        
        # Attach body
        message.attach(MIMEText(body, 'html' if html else 'plain'))
        
        # Attach files
        if attachments:
            for file_path in attachments:
                self._attach_file(message, file_path)
        
        # Send via SMTP or Gmail API
        try:
            if self.gmail_service:
                return self._send_via_gmail_api(message, to, cc, bcc)
            else:
                return self._send_via_smtp(message, to, cc, bcc)
        except Exception as e:
            self.logger.error(f'Failed to send email: {e}')
            return {'status': 'error', 'error': str(e)}
    
    def _send_via_smtp(self, message: MIMEMultipart, to: str, cc: str, bcc: str) -> dict:
        """Send via SMTP"""
        if not self.email_address or not self.email_password:
            return {'status': 'error', 'error': 'Email credentials not configured'}
        
        # Build recipient list
        recipients = [to]
        if cc:
            recipients.extend(cc.split(','))
        if bcc:
            recipients.extend(bcc.split(','))
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.send_message(message)
            server.quit()
            
            result = {
                'status': 'success',
                'to': to,
                'subject': subject,
                'sent_at': datetime.now().isoformat()
            }
            self._log_email(result)
            return result
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _send_via_gmail_api(self, message: MIMEMultipart, to: str, cc: str, bcc: str) -> dict:
        """Send via Gmail API"""
        try:
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            sent_message = self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            result = {
                'status': 'success',
                'message_id': sent_message['id'],
                'to': to,
                'subject': message['Subject'],
                'sent_at': datetime.now().isoformat()
            }
            self._log_email(result)
            return result
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _attach_file(self, message: MIMEMultipart, file_path: str):
        """Attach a file to the message"""
        try:
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{Path(file_path).name}"'
                )
                message.attach(part)
        except Exception as e:
            self.logger.error(f'Failed to attach file {file_path}: {e}')
    
    def _dry_run_send(self, to: str, subject: str, body: str, cc: str, attachments: list) -> dict:
        """Simulate sending without actually sending"""
        self.logger.info(f'[DRY RUN] Would send email to: {to}')
        self.logger.info(f'[DRY RUN] Subject: {subject}')
        self.logger.info(f'[DRY RUN] Body: {body[:100]}...')
        if cc:
            self.logger.info(f'[DRY RUN] CC: {cc}')
        if attachments:
            self.logger.info(f'[DRY RUN] Attachments: {attachments}')
        
        return {
            'status': 'dry_run',
            'to': to,
            'subject': subject,
            'simulated_at': datetime.now().isoformat()
        }
    
    def _log_email(self, result: dict):
        """Log email to file"""
        log_file = self.logs_dir / f'{datetime.now().strftime("%Y-%m-%d")}.log'
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            **result
        }
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')


def main():
    parser = argparse.ArgumentParser(description='Send emails via SMTP or Gmail API')
    parser.add_argument('--to', required=True, help='Recipient email address')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--body', required=True, help='Email body text')
    parser.add_argument('--cc', help='CC email addresses (comma-separated)')
    parser.add_argument('--bcc', help='BCC email addresses (comma-separated)')
    parser.add_argument('--attachment', action='append', help='File to attach (can be specified multiple times)')
    parser.add_argument('--html', action='store_true', help='Body is HTML format')
    parser.add_argument('--vault', default='.', help='Path to Obsidian vault')
    
    args = parser.parse_args()
    
    sender = EmailSender(args.vault)
    result = sender.send(
        to=args.to,
        subject=args.subject,
        body=args.body,
        cc=args.cc,
        bcc=args.bcc,
        attachments=args.attachment,
        html=args.html
    )
    
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'success' else 1


if __name__ == '__main__':
    sys.exit(main())
