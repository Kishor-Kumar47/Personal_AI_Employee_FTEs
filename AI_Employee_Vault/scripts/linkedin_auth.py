"""
LinkedIn Authentication Helper

This script helps you authenticate with LinkedIn manually.
It will open a browser, you log in, and then it saves your session.

Usage:
    python linkedin_auth.py
"""

import sys
import io
import json
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed. Run: pip install playwright")
    sys.exit(1)


def authenticate_linkedin(session_path: str = None):
    """Open browser and authenticate with LinkedIn"""
    
    session_dir = Path(session_path) if session_path else (
        Path(__file__).parent / '.linkedin_session'
    )
    session_dir.mkdir(parents=True, exist_ok=True)
    cookie_file = session_dir / 'cookies.json'
    
    print('=' * 60)
    print('LinkedIn Authentication')
    print('=' * 60)
    print()
    print('This will open a browser window.')
    print()
    print('Steps:')
    print('1. Log in to LinkedIn in the browser window')
    print('2. Wait for your feed to load completely')
    print('3. Come back to this window and press Enter')
    print()
    print('Opening browser...')
    print()
    
    with sync_playwright() as p:
        # Launch browser in visible mode
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )
        
        # Create context with realistic user agent
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        
        # Go to LinkedIn
        print('Navigate to: https://www.linkedin.com')
        page.goto('https://www.linkedin.com', timeout=60000)
        
        print()
        print('Browser opened. Please log in to LinkedIn...')
        print()
        
        # Wait for user to login
        try:
            input('Press Enter after you have successfully logged in...')
        except:
            pass
        
        # Check if logged in
        is_logged_in = False
        try:
            # Look for profile menu or feed
            selectors = [
                '[data-control-name="nav.settings"]',
                '[aria-label="You"]',
                '.mn-navigation-indicator'
            ]
            
            for selector in selectors:
                if page.query_selector(selector):
                    is_logged_in = True
                    break
            
            if not is_logged_in:
                is_logged_in = 'feed' in page.url.lower()
        except:
            pass
        
        if is_logged_in:
            print()
            print('✅ Login detected!')
            print()
            
            # Get cookies
            cookies = context.cookies()
            linkedin_cookies = [c for c in cookies if 'linkedin' in c.get('domain', '')]
            
            # Save cookies
            cookie_file.write_text(json.dumps(linkedin_cookies, indent=2))
            
            print(f'Saved {len(linkedin_cookies)} LinkedIn cookies to:')
            print(f'  {cookie_file}')
            print()
            print('You can now use the LinkedIn Watcher!')
            print()
            print('Test it with:')
            print('  python linkedin_watcher.py "../" --once')
        else:
            print()
            print('❌ Login not detected. Please try again.')
            print('   Make sure you are logged in to LinkedIn.')
        
        browser.close()


if __name__ == '__main__':
    authenticate_linkedin()
