"""
LinkedIn Authentication Helper - Manual Mode

This script opens LinkedIn in your default browser for manual login.
After logging in, it extracts cookies using a different method.

Usage:
    python linkedin_auth_manual.py
"""

import sys
import io
import json
import time
from pathlib import Path
import webbrowser

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def authenticate_linkedin_manual():
    """
    Open LinkedIn in your default browser for manual authentication.
    
    Since automated browser detection is an issue, we'll use a 
    semi-manual approach.
    """
    
    session_dir = Path(__file__).parent / '.linkedin_session'
    session_dir.mkdir(parents=True, exist_ok=True)
    cookie_file = session_dir / 'cookies.json'
    
    print('=' * 60)
    print('LinkedIn Authentication - Manual Method')
    print('=' * 60)
    print()
    print('Due to browser automation detection, we\'ll use a manual approach.')
    print()
    print('INSTRUCTIONS:')
    print()
    print('1. A browser window will open to LinkedIn')
    print('2. Log in to your LinkedIn account')
    print('3. Wait for your feed to fully load')
    print('4. Press Enter in this window when ready')
    print('5. The script will attempt to capture your session')
    print()
    print('NOTE: If automatic cookie capture fails, you may need to')
    print('      use LinkedIn\'s "Remember me" option for future visits.')
    print()
    
    input('Press Enter to open LinkedIn in your browser...')
    
    # Open LinkedIn in default browser
    print()
    print('Opening LinkedIn in your default browser...')
    webbrowser.open('https://www.linkedin.com')
    
    print()
    print('Please log in to LinkedIn.')
    print('After you\'re logged in and see your feed, press Enter below.')
    print()
    
    input('Press Enter when you are logged in to LinkedIn...')
    
    print()
    print('Attempting to capture session...')
    print()
    
    # Try to capture with Playwright
    if PLAYWRIGHT_AVAILABLE:
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(
                    headless=False,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--no-sandbox',
                        '--disable-gpu'
                    ]
                )
                
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                
                page = context.new_page()
                
                # Navigate with longer timeout
                print('Loading LinkedIn...')
                page.goto('https://www.linkedin.com', timeout=120000, wait_until='networkidle')
                
                # Wait a bit for page to stabilize
                time.sleep(5)
                
                # Check if logged in
                is_logged_in = False
                try:
                    selectors = [
                        '[data-control-name="nav.settings"]',
                        '[aria-label="You"]',
                        '.mn-navigation-indicator',
                        'a[href*="/mynetwork/"]',
                        'a[href*="/messaging/"]'
                    ]
                    
                    for selector in selectors:
                        if page.query_selector(selector):
                            is_logged_in = True
                            print(f'Found element: {selector}')
                            break
                    
                    if not is_logged_in:
                        current_url = page.url
                        if 'feed' in current_url.lower() or 'linkedin.com/feed' in current_url:
                            is_logged_in = True
                            print(f'URL indicates logged in: {current_url}')
                except Exception as e:
                    print(f'Error checking login status: {e}')
                
                if is_logged_in:
                    print()
                    print('✅ Login detected!')
                    print()
                    
                    # Get and save cookies
                    cookies = context.cookies()
                    linkedin_cookies = [c for c in cookies if 'linkedin' in c.get('domain', '')]
                    
                    cookie_file.write_text(json.dumps(linkedin_cookies, indent=2))
                    
                    print(f'Saved {len(linkedin_cookies)} LinkedIn cookies')
                    print(f'Location: {cookie_file}')
                    print()
                    print('SUCCESS! You can now use the LinkedIn Watcher.')
                    print()
                    print('Test with:')
                    print('  python linkedin_watcher.py "../" --once')
                else:
                    print()
                    print('❌ Could not detect login.')
                    print()
                    print('TROUBLESHOOTING:')
                    print('1. Make sure you logged in to LinkedIn')
                    print('2. Wait for your feed to fully load')
                    print('3. Try running this script again')
                    print()
                    print('Alternative: Use the LinkedIn Poster skill directly')
                    print('  python linkedin_poster.py --login')
                
                browser.close()
                
        except Exception as e:
            print(f'Error during authentication: {e}')
            print()
            print('FALLBACK METHOD:')
            print('Since automated capture is not working, please:')
            print('1. Keep LinkedIn open in your browser')
            print('2. Use the LinkedIn Poster skill which will open its own browser')
            print('3. Or use the LinkedIn website directly for now')
    else:
        print('Playwright not available. Please install:')
        print('  pip install playwright && playwright install chromium')
    
    print()
    print('=' * 60)


if __name__ == '__main__':
    authenticate_linkedin_manual()
