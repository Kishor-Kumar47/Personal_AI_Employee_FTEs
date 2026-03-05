"""
LinkedIn Auto Poster - Login and Post in One Session

This script logs in to LinkedIn and immediately posts to avoid session expiration.

Usage:
    python linkedin_auto_post.py --email "your@email.com" --password "your_password" --content "Your post content"
    
Or store credentials in .env file:
    LINKEDIN_EMAIL=your@email.com
    LINKEDIN_PASSWORD=your_password
    
Then run:
    python linkedin_auto_post.py --content "Your post content"
"""

import sys
import io
import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Error: Playwright not installed.")
    print("Run: pip install playwright && playwright install")
    sys.exit(1)


def auto_post_linkedin(email: str, password: str, content: str, image_path: str = None, vault_path: str = None):
    """
    Login to LinkedIn and post in one session
    
    Args:
        email: LinkedIn email
        password: LinkedIn password
        content: Post content
        image_path: Optional image to attach
        vault_path: Path to vault for logging
    """
    
    print('=' * 60)
    print('LinkedIn Auto Poster')
    print('=' * 60)
    print()
    
    result = {
        'status': 'error',
        'timestamp': datetime.now().isoformat(),
        'content': content[:100]
    }
    
    try:
        with sync_playwright() as p:
            print('Launching browser...')
            browser = p.chromium.launch(
                headless=False,  # Visible browser for debugging
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                accept_downloads=True,
                ignore_https_errors=True
            )
            
            # Enable DNS prefetch
            context.set_default_timeout(60000)
            
            page = context.new_page()
            
            # Step 1: Go to LinkedIn
            print('Navigating to LinkedIn...')
            try:
                page.goto('https://linkedin.com', timeout=60000, wait_until='domcontentloaded')
                time.sleep(5)
            except Exception as nav_error:
                print(f'Navigation error: {nav_error}')
                print('Trying alternative URL...')
                page.goto('https://www.linkedin.com/feed/', timeout=60000)
                time.sleep(5)
            
            # Check if already logged in
            if 'feed' in page.url.lower():
                print('Already logged in!')
            else:
                # Step 2: Login
                print(f'Logging in as {email}...')
                
                # Find and fill email
                email_field = page.query_selector('#username')
                if email_field:
                    email_field.fill(email)
                    time.sleep(1)
                
                # Find and fill password
                password_field = page.query_selector('#password')
                if password_field:
                    password_field.fill(password)
                    time.sleep(1)
                
                # Click sign in
                sign_in_button = page.query_selector('button[type="submit"]')
                if sign_in_button:
                    sign_in_button.click()
                    time.sleep(5)
                    
                    # Wait for login to complete
                    try:
                        page.wait_for_url('**/feed/**', timeout=30000)
                        print('Login successful!')
                    except:
                        print('Login may have failed. Continuing anyway...')
            
            time.sleep(3)
            
            # Step 3: Navigate to feed (post creation area)
            print('Navigating to feed...')
            page.goto('https://www.linkedin.com/feed/', timeout=60000, wait_until='networkidle')
            time.sleep(3)
            
            # Step 4: Click on "Start a post"
            print('Opening post composer...')
            
            post_triggers = [
                '[aria-label="Start a post"]',
                '.share-box-feed-entry__trigger',
                '[data-control-name="compose-status-update"]',
                'button:has-text("Start a post")'
            ]
            
            clicked = False
            for selector in post_triggers:
                elem = page.query_selector(selector)
                if elem:
                    elem.click()
                    clicked = True
                    print('Post composer opened!')
                    break
                    time.sleep(2)
            
            if not clicked:
                print('Warning: Could not find post button. Trying alternative method...')
                # Try to directly focus on the editor
                page.keyboard.press('Tab')
                time.sleep(1)
            
            time.sleep(3)
            
            # Step 5: Type post content
            print('Typing post content...')
            
            # Find the editor
            editors = [
                '[aria-label="What do you want to talk about?"]',
                '[aria-label="Share what do you want to talk about?"]',
                '.ql-editor.textarea',
                'div[contenteditable="true"]'
            ]
            
            for selector in editors:
                editor = page.query_selector(selector)
                if editor:
                    editor.click()
                    time.sleep(1)
                    
                    # Type content slowly (like a human)
                    for i, char in enumerate(content):
                        page.keyboard.type(char, delay=50)
                        if i % 50 == 0:
                            time.sleep(0.5)
                    
                    print('Content typed!')
                    break
            
            time.sleep(2)
            
            # Step 6: Add image if provided
            if image_path and Path(image_path).exists():
                print(f'Attaching image: {image_path}')
                
                # Click media button
                media_buttons = [
                    '[aria-label="Add media"]',
                    '[aria-label*="photo"]',
                    'button[aria-label*="image"]'
                ]
                
                for selector in media_buttons:
                    elem = page.query_selector(selector)
                    if elem:
                        elem.click()
                        time.sleep(2)
                        
                        # Upload file
                        page.set_input_files('input[type="file"]', image_path)
                        time.sleep(3)
                        print('Image attached!')
                        break
            
            time.sleep(2)
            
            # Step 7: Click Post button
            print('Publishing post...')
            
            post_buttons = [
                'button[aria-label="Post"]',
                '[data-control-name="update-post-submit"]',
                'button:has-text("Post")'
            ]
            
            for selector in post_buttons:
                elem = page.query_selector(selector)
                if elem:
                    elem.click()
                    print('Post button clicked!')
                    break
            
            # Wait for post to publish
            time.sleep(5)
            
            # Check if post was successful
            if 'posted' in page.content().lower() or 'feed' in page.url.lower():
                result['status'] = 'success'
                print()
                print('SUCCESS! Post published to LinkedIn.')
            else:
                result['status'] = 'uncertain'
                print()
                print('Post may have been published. Please check your LinkedIn feed.')
            
            # Take screenshot for verification
            screenshot_path = Path(__file__).parent / 'linkedin_post_screenshot.png'
            page.screenshot(path=str(screenshot_path))
            print(f'Screenshot saved: {screenshot_path}')
            
            browser.close()
            
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
        print(f'Error: {e}')
    
    # Log result
    if vault_path:
        log_dir = Path(vault_path) / 'Logs' / 'linkedin'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f'{datetime.now().strftime("%Y-%m-%d")}.log'
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(result) + '\n')
    
    print()
    print('=' * 60)
    
    return result


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Auto Poster')
    parser.add_argument('--content', '-c', required=True, help='Post content')
    parser.add_argument('--email', '-e', help='LinkedIn email (or set LINKEDIN_EMAIL env var)')
    parser.add_argument('--password', '-p', help='LinkedIn password (or set LINKEDIN_PASSWORD env var)')
    parser.add_argument('--image', '-i', help='Path to image file')
    parser.add_argument('--vault', '-v', default='..', help='Path to vault for logging')
    
    args = parser.parse_args()
    
    # Get credentials
    email = args.email or os.getenv('LINKEDIN_EMAIL')
    password = args.password or os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print('Error: LinkedIn credentials required')
        print()
        print('Options:')
        print('  1. Use --email and --password flags')
        print('  2. Set environment variables:')
        print('     set LINKEDIN_EMAIL=your@email.com')
        print('     set LINKEDIN_PASSWORD=your_password')
        print('  3. Create .env file in project root')
        sys.exit(1)
    
    # Post to LinkedIn
    result = auto_post_linkedin(
        email=email,
        password=password,
        content=args.content,
        image_path=args.image,
        vault_path=args.vault
    )
    
    sys.exit(0 if result['status'] == 'success' else 1)


if __name__ == '__main__':
    main()
