"""
LinkedIn Watcher - Monitors LinkedIn for notifications and messages

This watcher uses Playwright to monitor LinkedIn for:
- New connection requests
- Messages
- Job opportunities
- Post engagement (likes, comments)

Usage:
    python linkedin_watcher.py /path/to/vault

Prerequisites:
    - Playwright installed: pip install playwright
    - Playwright browsers: playwright install
    - LinkedIn session cookie or login credentials
"""

import sys
import os
import io
import time
import json
import logging
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding for Unicode emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path for base_watcher import
sys.path.insert(0, str(Path(__file__).parent))

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not installed.")
    print("Run: pip install playwright && playwright install")

from base_watcher import BaseWatcher


class LinkedInWatcher(BaseWatcher):
    """Watches LinkedIn for new notifications and messages"""
    
    def __init__(self, vault_path: str, session_path: str = None, check_interval: int = 300):
        """
        Initialize LinkedIn watcher
        
        Args:
            vault_path: Path to the Obsidian vault
            session_path: Path to store session cookies
            check_interval: Seconds between checks (default: 300 = 5 min)
        """
        super().__init__(vault_path, check_interval)
        
        self.session_path = Path(session_path) if session_path else (
            Path(__file__).parent / '.linkedin_session'
        )
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        self.cookie_file = self.session_path / 'cookies.json'
        self.processed_file = self.session_path / 'processed.json'
        
        # Load processed items
        self.processed_ids = set()
        self._load_processed_ids()
        
        # Keywords for priority detection
        self.priority_keywords = [
            'hiring', 'job', 'opportunity', 'interview', 'position',
            'connection', 'message', 'inbox', 'recommendation'
        ]
        
        # LinkedIn URLs
        self.linkedin_url = 'https://www.linkedin.com'
        self.notifications_url = 'https://www.linkedin.com/notifications'
        self.messaging_url = 'https://www.linkedin.com/messaging'
    
    def _load_processed_ids(self):
        """Load previously processed item IDs"""
        if self.processed_file.exists():
            try:
                data = json.loads(self.processed_file.read_text())
                self.processed_ids = set(data.get('ids', []))
            except:
                self.processed_ids = set()
    
    def _save_processed_ids(self):
        """Save processed item IDs"""
        try:
            ids = list(self.processed_ids)[-500:]
            self.processed_file.write_text(json.dumps({'ids': ids, 'updated': datetime.now().isoformat()}))
        except Exception as e:
            self.logger.error(f'Error saving processed IDs: {e}')
    
    def _save_cookies(self, context):
        """Save browser cookies"""
        try:
            cookies = context.cookies()
            linkedin_cookies = [c for c in cookies if 'linkedin' in c.get('domain', '')]
            self.cookie_file.write_text(json.dumps(linkedin_cookies))
            self.logger.debug('Saved LinkedIn cookies')
        except Exception as e:
            self.logger.error(f'Error saving cookies: {e}')
    
    def _load_cookies(self):
        """Load saved browser cookies"""
        if self.cookie_file.exists():
            try:
                cookies = json.loads(self.cookie_file.read_text())
                return cookies
            except:
                pass
        return []
    
    def check_for_updates(self) -> list:
        """
        Check LinkedIn for new notifications and messages
        
        Returns:
            list: List of new notification dicts
        """
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error('Playwright not available')
            return []
        
        new_items = []
        
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                # Create context with user agent
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                
                # Load saved cookies
                cookies = self._load_cookies()
                if cookies:
                    context.add_cookies(cookies)
                    self.logger.info('Loaded saved session cookies')
                
                page = context.new_page()
                
                # Navigate to LinkedIn
                try:
                    page.goto(self.linkedin_url, timeout=30000, wait_until='networkidle')
                except PlaywrightTimeout:
                    self.logger.warning('LinkedIn page load timeout')
                    browser.close()
                    return []
                
                # Check if logged in
                is_logged_in = self._check_logged_in(page)
                
                if not is_logged_in:
                    self.logger.warning('Not logged in to LinkedIn. Please login manually or check session.')
                    # Save screenshot for debugging
                    page.screenshot(path=str(self.session_path / 'login_required.png'))
                    browser.close()
                    return []
                
                # Save cookies after successful login check
                self._save_cookies(context)
                
                # Check notifications
                try:
                    notifications = self._get_notifications(page)
                    for notif in notifications:
                        if notif['id'] not in self.processed_ids:
                            new_items.append(notif)
                            self.processed_ids.add(notif['id'])
                except Exception as e:
                    self.logger.error(f'Error getting notifications: {e}')
                
                # Check messages
                try:
                    messages = self._get_messages(page)
                    for msg in messages:
                        if msg['id'] not in self.processed_ids:
                            new_items.append(msg)
                            self.processed_ids.add(msg['id'])
                except Exception as e:
                    self.logger.error(f'Error getting messages: {e}')
                
                browser.close()
                
                # Save processed IDs
                if new_items:
                    self._save_processed_ids()
                    self.logger.info(f'Found {len(new_items)} new LinkedIn item(s)')
                
                return new_items
                
        except Exception as e:
            self.logger.error(f'Error in LinkedIn watcher: {e}')
            return []
    
    def _check_logged_in(self, page) -> bool:
        """Check if user is logged in to LinkedIn"""
        try:
            # Look for profile icon or feed
            selectors = [
                '[data-control-name="nav.settings"]',
                '.mn-navigation-indicator',
                '#global-nav',
                '[aria-label="You"]'
            ]
            
            for selector in selectors:
                if page.query_selector(selector):
                    return True
            
            # Check for login page indicators
            if 'login' in page.url.lower():
                return False
            
            # Wait a bit and check again
            page.wait_for_timeout(2000)
            return 'feed' in page.url.lower() or page.query_selector('[data-control-name="nav.settings"]')
            
        except:
            return False
    
    def _get_notifications(self, page) -> list:
        """Get recent notifications"""
        notifications = []
        
        try:
            # Navigate to notifications page
            page.goto(self.notifications_url, timeout=15000, wait_until='networkidle')
            page.wait_for_timeout(3000)
            
            # Find notification items
            notif_selectors = [
                'ul.mn-notification-list > li',
                '[data-test-notif-list-item]',
                '.mn-notification-list-item'
            ]
            
            notif_elements = []
            for selector in notif_selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    notif_elements = elements
                    break
            
            for i, elem in enumerate(notif_elements[:10]):  # Limit to 10
                try:
                    text = elem.inner_text()
                    time_elem = elem.query_selector('time')
                    timestamp = time_elem.get_attribute('datetime') if time_elem else datetime.now().isoformat()
                    
                    notifications.append({
                        'id': f'linkedin_notif_{i}_{int(datetime.now().timestamp())}',
                        'type': 'notification',
                        'content': text[:500],
                        'timestamp': timestamp,
                        'source': 'linkedin'
                    })
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f'Error fetching notifications: {e}')
        
        return notifications
    
    def _get_messages(self, page) -> list:
        """Get recent messages"""
        messages = []
        
        try:
            # Navigate to messaging
            page.goto(self.messaging_url, timeout=15000, wait_until='networkidle')
            page.wait_for_timeout(3000)
            
            # Find conversation items
            convo_selectors = [
                'ul.conversations-list > li',
                '[data-test-conversation-item]',
                '.msg-conversations-list__item'
            ]
            
            convo_elements = []
            for selector in convo_selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    convo_elements = elements
                    break
            
            for i, elem in enumerate(convo_elements[:5]):  # Limit to 5
                try:
                    text = elem.inner_text()
                    
                    # Check if unread
                    is_unread = 'unread' in elem.get_attribute('class', '').lower()
                    
                    if is_unread:  # Only process unread messages
                        messages.append({
                            'id': f'linkedin_msg_{i}_{int(datetime.now().timestamp())}',
                            'type': 'message',
                            'content': text[:500],
                            'timestamp': datetime.now().isoformat(),
                            'source': 'linkedin',
                            'priority': 'high'
                        })
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f'Error fetching messages: {e}')
        
        return messages
    
    def create_action_file(self, item) -> Path:
        """
        Create an action file for the LinkedIn item
        
        Args:
            item: LinkedIn notification/message dict
            
        Returns:
            Path: Path to the created action file
        """
        try:
            item_type = item.get('type', 'unknown')
            content = item.get('content', '')
            priority = item.get('priority', 'normal')
            
            # Determine priority based on content
            if priority == 'normal':
                for keyword in self.priority_keywords:
                    if keyword in content.lower():
                        priority = 'high'
                        break
            
            action_file_name = f'LINKEDIN_{item["id"]}_{item_type}.md'
            action_file_path = self.needs_action / action_file_name
            
            file_content = f'''---
type: linkedin_{item_type}
source: linkedin
item_id: {item['id']}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
---

# LinkedIn {item_type.title()}

## Received
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Content
{content}

## Suggested Actions
- [ ] Review the {item_type}
- [ ] Determine required response
- [ ] Check Company_Handbook.md for response rules
{('- [ ] Respond to message' if item_type == 'message' else '- [ ] Take appropriate action')}
- [ ] Create approval request if needed
- [ ] Move to /Done when complete

## Notes
_Add your notes here_

## Response Draft
_Draft your response here if needed_

---
*Processed by LinkedIn Watcher v1.0 (Silver Tier)*
'''
            
            action_file_path.write_text(file_content, encoding='utf-8')
            
            self.logger.info(f'Created action file: {action_file_name}')
            return action_file_path
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            raise


def main():
    if len(sys.argv) < 2:
        print('Usage: python linkedin_watcher.py <vault_path>')
        print('Example: python linkedin_watcher.py "C:/AI_Employee_Vault"')
        print()
        print('Options:')
        print('  --once    Run once and exit (for testing)')
        print('  --login   Open browser for manual login')
        sys.exit(1)
    
    vault_path = Path(sys.argv[1]).expanduser().resolve()
    
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    # Check for flags
    run_once = '--once' in sys.argv
    login_mode = '--login' in sys.argv
    
    watcher = LinkedInWatcher(str(vault_path))
    
    print(f'🔗 LinkedIn Watcher started')
    print(f'   Vault: {vault_path}')
    print(f'   Session: {watcher.session_path}')
    print(f'   Check interval: {watcher.check_interval}s')
    if run_once:
        print(f'   Mode: Run once')
    if login_mode:
        print(f'   Mode: Login mode (interactive)')
    else:
        print(f'   Press Ctrl+C to stop')
    print()
    
    if not PLAYWRIGHT_AVAILABLE:
        print('❌ Playwright not available. Install with: pip install playwright && playwright install')
        sys.exit(1)
    
    if login_mode:
        # Interactive login mode
        print('Opening browser for LinkedIn login...')
        print('Please log in to LinkedIn, then close the browser.')
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            page.goto('https://www.linkedin.com')
            
            # Wait for user to close
            try:
                input('Press Enter after you have logged in and want to close the browser...')
            except:
                pass
            
            # Save cookies
            cookies = context.cookies()
            linkedin_cookies = [c for c in cookies if 'linkedin' in c.get('domain', '')]
            watcher.cookie_file.write_text(json.dumps(linkedin_cookies))
            print(f'✅ Saved {len(linkedin_cookies)} LinkedIn cookies')
            
            browser.close()
    elif run_once:
        # Run once for testing
        items = watcher.check_for_updates()
        print(f'Found {len(items)} new item(s)')
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
            print('\n👋 Stopping LinkedIn watcher...')
            watcher._save_processed_ids()


if __name__ == '__main__':
    main()
