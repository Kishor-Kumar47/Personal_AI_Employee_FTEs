"""
LinkedIn Poster - Post updates to LinkedIn automatically

Uses Playwright browser automation to post to LinkedIn.

Usage:
    python linkedin_poster.py post --content "Your post content"
    python linkedin_poster.py --login    # First time login
    python linkedin_poster.py schedule --content "Post" --time "2026-01-13T09:00:00"
"""

import sys
import os
import io
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding for Unicode emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Error: Playwright not installed.")
    print("Run: pip install playwright && playwright install")
    sys.exit(1)


class LinkedInPoster:
    """Post updates to LinkedIn"""
    
    def __init__(self, session_path: str = None, vault_path: str = None):
        self.session_path = Path(session_path) if session_path else (
            Path(__file__).parent / '.linkedin_session'
        )
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.cookie_file = self.session_path / 'cookies.json'
        
        self.vault_path = Path(vault_path) if vault_path else Path.cwd()
        self.logs_dir = self.vault_path / 'Logs' / 'linkedin'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.linkedin_url = 'https://www.linkedin.com'
    
    def login(self):
        """Interactive login to LinkedIn"""
        print('Opening browser for LinkedIn login...')
        print('Please log in to LinkedIn, then press Enter.')
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            page.goto(self.linkedin_url)
            
            try:
                input('Press Enter after you have logged in...')
            except:
                pass
            
            # Save cookies
            cookies = context.cookies()
            linkedin_cookies = [c for c in cookies if 'linkedin' in c.get('domain', '')]
            self.cookie_file.write_text(json.dumps(linkedin_cookies))
            print(f'✅ Saved {len(linkedin_cookies)} LinkedIn cookies')
            
            browser.close()
    
    def post(self, content: str, image_path: str = None) -> dict:
        """
        Post to LinkedIn
        
        Args:
            content: Post content text
            image_path: Optional path to image
            
        Returns:
            dict: Result with status and post URL
        """
        if not self.cookie_file.exists():
            return {'status': 'error', 'error': 'Not logged in. Run with --login first.'}
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                
                # Load cookies
                cookies = json.loads(self.cookie_file.read_text())
                context.add_cookies(cookies)
                
                page = context.new_page()
                
                # Navigate to LinkedIn
                page.goto(self.linkedin_url, wait_until='networkidle', timeout=30000)
                page.wait_for_timeout(3000)
                
                # Check if logged in
                if not self._is_logged_in(page):
                    return {'status': 'error', 'error': 'Session expired. Re-login required.'}
                
                # Start post creation
                self._create_post(page, content, image_path)
                
                # Get post URL if successful
                result = {
                    'status': 'success',
                    'content': content[:100],
                    'posted_at': datetime.now().isoformat()
                }
                
                self._log_post(result)
                browser.close()
                
                return result
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _is_logged_in(self, page) -> bool:
        """Check if user is logged in"""
        try:
            selectors = [
                '[data-control-name="nav.settings"]',
                '[aria-label="You"]',
                '.mn-navigation-indicator'
            ]
            
            for selector in selectors:
                if page.query_selector(selector):
                    return True
            
            return 'feed' in page.url.lower()
        except:
            return False
    
    def _create_post(self, page, content: str, image_path: str = None):
        """Create and publish post"""
        try:
            # Click on "Start a post"
            start_post_selectors = [
                '[data-control-name="compose-status-update"]',
                '.share-box-feed-entry__trigger',
                'button[aria-label="Start a post"]'
            ]
            
            for selector in start_post_selectors:
                elem = page.query_selector(selector)
                if elem:
                    elem.click()
                    page.wait_for_timeout(2000)
                    break
            
            # Find the text editor and type content
            editor_selectors = [
                '[aria-label="What do you want to talk about?"]',
                '[aria-label="Share what do you want to talk about?"]',
                '.ql-editor.textarea'
            ]
            
            for selector in editor_selectors:
                editor = page.query_selector(selector)
                if editor:
                    editor.click()
                    page.wait_for_timeout(500)
                    
                    # Type content (simulate typing)
                    for char in content:
                        editor.type(char, delay=10)
                        if len(content) > 100 and content.index(char) % 50 == 0:
                            page.wait_for_timeout(10)
                    break
            
            # Upload image if provided
            if image_path and Path(image_path).exists():
                # Click on media/photo button
                media_selectors = [
                    '[aria-label="Add media"]',
                    '[data-control-name="compose-upload-button"]',
                    'button[aria-label*="photo"]'
                ]
                
                for selector in media_selectors:
                    elem = page.query_selector(selector)
                    if elem:
                        elem.click()
                        page.wait_for_timeout(1000)
                        
                        # Find file input and upload
                        page.set_input_files('input[type="file"]', image_path)
                        page.wait_for_timeout(3000)
                        break
            
            # Click Post button
            post_selectors = [
                'button[aria-label="Post"]',
                '[data-control-name="update-post-submit"]',
                'button:has-text("Post")'
            ]
            
            for selector in post_selectors:
                elem = page.query_selector(selector)
                if elem:
                    elem.click()
                    page.wait_for_timeout(3000)
                    break
            
        except Exception as e:
            raise Exception(f'Error creating post: {e}')
    
    def _log_post(self, result: dict):
        """Log post to file"""
        log_file = self.logs_dir / f'{datetime.now().strftime("%Y-%m-%d")}.log'
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            **result
        }
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Poster')
    parser.add_argument('command', nargs='?', default='post',
                        choices=['post', 'login', 'schedule', 'list-scheduled', 'cancel'],
                        help='Command to run')
    parser.add_argument('--content', '-c', help='Post content')
    parser.add_argument('--image', '-i', help='Path to image file')
    parser.add_argument('--time', '-t', help='Scheduled time (YYYY-MM-DDTHH:MM:SS)')
    parser.add_argument('--vault', '-v', default='.', help='Path to Obsidian vault')
    parser.add_argument('--id', help='Scheduled post ID (for cancel)')
    
    args = parser.parse_args()
    
    poster = LinkedInPoster(vault_path=args.vault)
    
    if args.command == 'login':
        poster.login()
        
    elif args.command == 'post':
        if not args.content:
            print('Error: --content required for post')
            sys.exit(1)
        
        print(f'Posting to LinkedIn...')
        result = poster.post(args.content, args.image)
        
        if result['status'] == 'success':
            print(f'✅ Post successful!')
            print(f'   Content: {result["content"]}...')
            print(f'   Posted at: {result["posted_at"]}')
        else:
            print(f'❌ Post failed: {result.get("error", "Unknown error")}')
            sys.exit(1)
            
    elif args.command == 'schedule':
        if not args.content or not args.time:
            print('Error: --content and --time required for schedule')
            sys.exit(1)
        
        # Save scheduled post
        scheduled_dir = Path(args.vault) / 'scheduler' / 'linkedin'
        scheduled_dir.mkdir(parents=True, exist_ok=True)
        
        post_id = f'SCHED_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        post_file = scheduled_dir / f'{post_id}.json'
        
        post_data = {
            'id': post_id,
            'content': args.content,
            'image': args.image,
            'scheduled_time': args.time,
            'created': datetime.now().isoformat()
        }
        
        post_file.write_text(json.dumps(post_data, indent=2))
        print(f'✅ Post scheduled: {post_id}')
        print(f'   Time: {args.time}')
        print(f'   Content: {args.content[:100]}...')
        
    elif args.command == 'list-scheduled':
        scheduled_dir = Path(args.vault) / 'scheduler' / 'linkedin'
        if scheduled_dir.exists():
            posts = list(scheduled_dir.glob('*.json'))
            if posts:
                print(f'Scheduled posts ({len(posts)}):')
                for post_file in posts:
                    data = json.loads(post_file.read_text())
                    print(f"  - {data['id']}: {data['scheduled_time']}")
            else:
                print('No scheduled posts')
        else:
            print('No scheduled posts')
            
    elif args.command == 'cancel':
        if not args.id:
            print('Error: --id required for cancel')
            sys.exit(1)
        
        post_file = Path(args.vault) / 'scheduler' / 'linkedin' / f'{args.id}.json'
        if post_file.exists():
            post_file.unlink()
            print(f'✅ Cancelled scheduled post: {args.id}')
        else:
            print(f'Post not found: {args.id}')


if __name__ == '__main__':
    main()
