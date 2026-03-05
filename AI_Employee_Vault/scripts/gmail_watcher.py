"""
Gmail Watcher - Monitors Gmail for new important emails

This watcher checks Gmail for unread/important messages and creates
action files in the Needs_Action folder for Qwen Code to process.

Usage:
    python gmail_watcher.py /path/to/vault

Prerequisites:
    - Gmail API credentials (credentials.json in project root)
    - First-time authorization creates token.json automatically
"""

import sys
import os
import io
import time
import logging
import base64
from pathlib import Path
from datetime import datetime
from email import message_from_bytes

# Fix Windows console encoding for Unicode emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path for base_watcher import
sys.path.insert(0, str(Path(__file__).parent))

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_API_AVAILABLE = True
except ImportError:
    GMAIL_API_AVAILABLE = False
    print("Warning: Gmail API libraries not installed.")
    print("Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")

from base_watcher import BaseWatcher


class GmailWatcher(BaseWatcher):
    """Watches Gmail for new important messages"""
    
    def __init__(self, vault_path: str, credentials_path: str = None, check_interval: int = 120):
        """
        Initialize Gmail watcher
        
        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to Gmail API credentials.json
            check_interval: Seconds between checks (default: 120)
        """
        super().__init__(vault_path, check_interval)
        
        # Look for credentials in multiple locations
        if credentials_path:
            self.credentials_path = Path(credentials_path)
        else:
            # Search for credentials.json in multiple locations
            possible_paths = [
                # Project root (where credentials.json should be)
                Path(__file__).parent.parent.parent / 'credentials.json',
                # Parent of vault
                Path(__file__).parent.parent / 'credentials.json',
                # Scripts folder
                Path(__file__).parent / 'credentials.json',
                # Current working directory
                Path.cwd() / 'credentials.json',
            ]
            for p in possible_paths:
                if p.exists():
                    self.credentials_path = p
                    self.logger.info(f'Found credentials: {p}')
                    break
            else:
                self.credentials_path = Path(__file__).parent.parent.parent / 'credentials.json'
        
        self.token_path = Path(__file__).parent / 'token.json'
        self.scopes = ['https://www.googleapis.com/auth/gmail.readonly']
        
        self.service = None
        self.processed_ids = set()
        
        # Load previously processed message IDs
        self._load_processed_ids()
        
        # Keywords that indicate high priority
        self.priority_keywords = [
            'urgent', 'asap', 'invoice', 'payment', 'important',
            'deadline', 'emergency', 'action required', 'review',
            'client', 'customer', 'order', 'purchase'
        ]
    
    def _load_processed_ids(self):
        """Load previously processed message IDs from file"""
        processed_file = self.vault_path / '.processed_emails.json'
        if processed_file.exists():
            try:
                import json
                data = json.loads(processed_file.read_text())
                self.processed_ids = set(data.get('ids', []))
            except:
                self.processed_ids = set()
    
    def _save_processed_ids(self):
        """Save processed message IDs to file"""
        processed_file = self.vault_path / '.processed_emails.json'
        try:
            import json
            # Keep only last 1000 IDs to prevent file growing too large
            ids = list(self.processed_ids)[-1000:]
            processed_file.write_text(json.dumps({'ids': ids, 'updated': datetime.now().isoformat()}))
        except Exception as e:
            self.logger.error(f'Error saving processed IDs: {e}')
    
    def authenticate(self) -> bool:
        """Authenticate with Gmail API"""
        if not GMAIL_API_AVAILABLE:
            self.logger.error('Gmail API libraries not available')
            return False
        
        if not self.credentials_path.exists():
            self.logger.error(f'Credentials file not found: {self.credentials_path}')
            self.logger.info('Please create credentials.json from Google Cloud Console')
            return False
        
        creds = None
        
        # Load existing token
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
                self.logger.info('Loaded existing token')
            except Exception as e:
                self.logger.warning(f'Error loading token: {e}')
                creds = None
        
        # Refresh or authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.logger.info('Refreshed expired token')
                except Exception as e:
                    self.logger.warning(f'Token refresh failed: {e}')
                    creds = None
            
            if not creds:
                self.logger.info('Starting Gmail authentication...')
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.scopes
                    )
                    creds = flow.run_local_server(port=0)
                    self.token_path.write_text(creds.to_json())
                    self.logger.info('Authentication successful - token saved')
                except Exception as e:
                    self.logger.error(f'Authentication failed: {e}')
                    return False
        
        try:
            # Use explicit discovery document URL to avoid userId issue
            self.service = build('gmail', 'v1', credentials=creds)
            # Test the connection
            profile = self.service.users().getProfile(userId='me').execute()
            self.logger.info(f'Gmail service connected: {profile.get("emailAddress")}')
            return True
        except Exception as e:
            self.logger.error(f'Failed to build Gmail service: {e}')
            return False
    
    def check_for_updates(self) -> list:
        """
        Check for new unread emails
        
        Returns:
            list: List of new message dicts
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            # Search for unread messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=20
            ).execute()
            
            messages = results.get('messages', [])
            new_messages = []
            
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    new_messages.append(msg)
                    self.processed_ids.add(msg['id'])
            
            # Save processed IDs
            if new_messages:
                self._save_processed_ids()
                self.logger.info(f'Found {len(new_messages)} new message(s)')
            
            return new_messages
            
        except HttpError as error:
            self.logger.error(f'Gmail API error: {error}')
            # Try to re-authenticate on error
            self.service = None
            return []
        except Exception as e:
            self.logger.error(f'Error checking for updates: {e}')
            return []
    
    def create_action_file(self, message) -> Path:
        """
        Create an action file for the email
        
        Args:
            message: Gmail message dict
            
        Returns:
            Path: Path to the created action file
        """
        try:
            # Get full message details
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            from_email = headers.get('From', 'Unknown')
            subject = headers.get('Subject', 'No Subject')
            date = headers.get('Date', '')
            
            # Determine priority
            priority = self._determine_priority(subject, from_email)
            
            # Extract body
            body = self._extract_body(msg['payload'])
            
            # Get snippet
            snippet = msg.get('snippet', '')
            
            # Create action file content
            content = f'''---
type: email
source: gmail
message_id: {message['id']}
from: {from_email}
subject: {subject}
date: {date}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
snippet: {snippet}
---

# Email: {subject}

## Sender
**From:** {from_email}

## Date
{date}

## Preview
{snippet}

## Content
{body}

## Suggested Actions
- [ ] Read and understand the email
- [ ] Determine required response
- [ ] Check Company_Handbook.md for response rules
- [ ] Draft reply or take action
- [ ] Create approval request if needed
- [ ] Mark email as read when done
- [ ] Move to /Done when complete

## Notes
_Add your notes here_

---
*Processed by Gmail Watcher v1.0 (Silver Tier)*
'''
            
            # Create safe filename
            safe_subject = subject[:30].replace(' ', '_').replace('/', '_').replace('\\', '_')
            safe_subject = ''.join(c for c in safe_subject if c.isalnum() or c in '_-')
            action_file_name = f'EMAIL_{message["id"]}_{safe_subject}.md'
            action_file_path = self.needs_action / action_file_name
            
            action_file_path.write_text(content, encoding='utf-8')
            
            self.logger.info(f'Created action file: {action_file_name}')
            return action_file_path
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            raise
    
    def _extract_body(self, payload) -> str:
        """Extract text body from message payload"""
        body_text = ''
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    body_data = part['body'].get('data', '')
                    if body_data:
                        body_text = base64.urlsafe_b64decode(body_data).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html':
                    # Fallback to HTML if no plain text
                    body_data = part['body'].get('data', '')
                    if body_data:
                        body_text = base64.urlsafe_b64decode(body_data).decode('utf-8')
            
            # If still no body, check nested parts
            if not body_text:
                for part in payload['parts']:
                    if 'parts' in part:
                        body_text = self._extract_body(part)
                        if body_text:
                            break
        
        if not body_text and 'body' in payload and 'data' in payload['body']:
            body_data = payload['body']['data']
            body_text = base64.urlsafe_b64decode(body_data).decode('utf-8')
        
        if not body_text:
            return '[No text content available]'
        
        # Truncate long bodies
        if len(body_text) > 5000:
            body_text = body_text[:5000] + '\n\n... [content truncated]'
        
        return body_text
    
    def _determine_priority(self, subject: str, from_email: str) -> str:
        """Determine email priority based on content"""
        text = f'{subject} {from_email}'.lower()
        
        for keyword in self.priority_keywords:
            if keyword in text:
                return 'high'
        
        return 'normal'
    
    def mark_as_read(self, message_id: str):
        """Mark a message as read"""
        if self.service:
            try:
                self.service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
                self.logger.info(f'Marked message {message_id} as read')
            except Exception as e:
                self.logger.error(f'Error marking message as read: {e}')


def main():
    if len(sys.argv) < 2:
        print('Usage: python gmail_watcher.py <vault_path>')
        print('Example: python gmail_watcher.py "C:/AI_Employee_Vault"')
        print()
        print('Options:')
        print('  --once    Run once and exit (for testing)')
        sys.exit(1)
    
    vault_path = Path(sys.argv[1]).expanduser().resolve()
    
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    # Check for --once flag
    run_once = '--once' in sys.argv
    
    watcher = GmailWatcher(str(vault_path))
    
    print(f'📧 Gmail Watcher started')
    print(f'   Vault: {vault_path}')
    print(f'   Credentials: {watcher.credentials_path}')
    print(f'   Check interval: {watcher.check_interval}s')
    if run_once:
        print(f'   Mode: Run once')
    else:
        print(f'   Press Ctrl+C to stop')
    print()
    
    # Initial authentication
    if not watcher.authenticate():
        print('Failed to authenticate with Gmail. Please check credentials.')
        print('Make sure credentials.json exists and is valid.')
        sys.exit(1)
    
    print('✅ Gmail authenticated successfully')
    print()
    
    if run_once:
        # Run once for testing
        items = watcher.check_for_updates()
        print(f'Found {len(items)} new message(s)')
        for item in items:
            try:
                path = watcher.create_action_file(item)
                print(f'  ✅ Created: {path.name}')
            except Exception as e:
                print(f'  ❌ Error: {e}')
    else:
        try:
            watcher.run()
        except KeyboardInterrupt:
            print('\n👋 Stopping Gmail watcher...')
            watcher._save_processed_ids()


if __name__ == '__main__':
    main()
