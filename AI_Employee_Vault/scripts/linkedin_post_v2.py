"""
LinkedIn Auto Poster v2 - More Reliable Version

This version:
- Opens browser visible so you can see what's happening
- Waits longer between actions
- Has better element detection
- Shows you exactly what's happening

Usage:
    python linkedin_post_v2.py --email "jolmusic12@gmail.com" --password "your_password" --content "Your post"
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


def post_to_linkedin(email: str, password: str, content: str):
    """Post to LinkedIn with better reliability"""
    
    print('=' * 70)
    print('LinkedIn Auto Poster v2')
    print('=' * 70)
    print()
    print(f'Email: {email}')
    print(f'Content: {content[:50]}...')
    print()
    
    result = {'status': 'error', 'timestamp': datetime.now().isoformat()}
    
    try:
        with sync_playwright() as p:
            # Launch visible browser
            print('🌐 Opening browser...')
            browser = p.chromium.launch(
                headless=False,  # IMPORTANT: Visible browser
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--start-maximized'
                ]
            )
            
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                ignore_https_errors=True
            )
            
            page = context.new_page()
            
            # Disable automation detection
            page.add_init_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
            
            # Step 1: Go to LinkedIn
            print('📍 Navigating to LinkedIn...')
            page.goto('https://www.linkedin.com', timeout=90000)
            time.sleep(5)
            
            # Check current URL
            current_url = page.url
            print(f'   Current URL: {current_url}')
            
            # Step 2: Login if needed
            if 'login' in current_url.lower() or 'checkpoint' in current_url.lower():
                print('🔐 Login page detected. Logging in...')
                
                # Wait for login form
                time.sleep(3)
                
                # Fill email
                print('   Entering email...')
                email_field = page.locator('#username').first
                if email_field:
                    email_field.fill(email)
                    time.sleep(2)
                
                # Fill password
                print('   Entering password...')
                password_field = page.locator('#password').first
                if password_field:
                    password_field.fill(password)
                    time.sleep(2)
                
                # Click sign in
                print('   Clicking Sign In...')
                sign_in = page.locator('button[type="submit"]').first
                if sign_in:
                    sign_in.click()
                    time.sleep(8)  # Wait for login to process
                
                # Wait for feed
                try:
                    page.wait_for_url('**/feed/**', timeout=30000)
                    print('✅ Login successful!')
                except:
                    print('⚠️ Login may still be processing...')
                
                time.sleep(5)
            
            # Check if logged in
            current_url = page.url
            if 'login' in current_url.lower():
                print()
                print('❌ Still on login page. Login failed.')
                print()
                print('MANUAL LOGIN REQUIRED:')
                print('1. Please log in manually in the browser window')
                print('2. Wait for your feed to load')
                print('3. Come back here and press Enter')
                input('Press Enter when you are logged in...')
                time.sleep(3)
            
            # Step 3: Navigate to feed
            print('📍 Going to feed...')
            page.goto('https://www.linkedin.com/feed/', timeout=90000, wait_until='domcontentloaded')
            time.sleep(5)
            
            # Step 4: Click "Start a post"
            print('✏️  Opening post composer...')
            
            # Try multiple selectors
            post_buttons = [
                'button[aria-label="Start a post"]',
                '.share-box-feed-entry__trigger',
                '[data-control-name="compose-status-update"]',
                'div[role="button"]:has-text("Start a post")',
                'button:has-text("Start")'
            ]
            
            clicked = False
            for selector in post_buttons:
                try:
                    elem = page.locator(selector).first
                    if elem.is_visible(timeout=5000):
                        elem.click()
                        clicked = True
                        print(f'   Clicked: {selector}')
                        break
                except:
                    continue
            
            if not clicked:
                print('   ⚠️ Could not find post button automatically')
                print()
                print('MANUAL HELP:')
                print('1. Click "Start a post" box in the browser yourself')
                print('2. Wait for the composer to open')
                print('3. Press Enter here')
                input('Press Enter when post composer is open...')
            
            time.sleep(3)
            
            # Step 5: Type content
            print('⌨️  Typing post content...')
            
            # Find editor
            editors = [
                '[aria-label="What do you want to talk about?"]',
                '[aria-label="Share what do you want to talk about?"]',
                '.ql-editor.textarea',
                'div[contenteditable="true"]'
            ]
            
            typed = False
            for selector in editors:
                try:
                    editor = page.locator(selector).first
                    if editor.is_visible(timeout=5000):
                        editor.click()
                        time.sleep(1)
                        
                        # Type content character by character (human-like)
                        print('   Typing...')
                        for i, char in enumerate(content):
                            page.keyboard.type(char, delay=30 + (i % 10) * 5)
                            if i % 30 == 0 and i > 0:
                                time.sleep(0.3)
                        
                        typed = True
                        print('   ✅ Content typed!')
                        break
                except Exception as e:
                    print(f'   Editor attempt failed: {e}')
                    continue
            
            if not typed:
                print('   ⚠️ Could not type automatically')
                print()
                print('MANUAL HELP:')
                print('1. Copy this text:')
                print(f'   {content}')
                print('2. Paste it into the LinkedIn post box')
                print('3. Press Enter when done')
                input('Press Enter when you have pasted the content...')
            
            time.sleep(3)
            
            # Step 6: Click Post button
            print('📤 Publishing post...')
            
            post_buttons = [
                'button[aria-label="Post"]',
                '[data-control-name="update-post-submit"]',
                'button:has-text("Post")',
                'button[class*="share-actions__post-button"]'
            ]
            
            for selector in post_buttons:
                try:
                    elem = page.locator(selector).first
                    if elem.is_visible(timeout=5000) and elem.is_enabled(timeout=5000):
                        print(f'   Clicking: {selector}')
                        elem.click()
                        time.sleep(5)
                        break
                except:
                    continue
            
            # Wait for confirmation
            time.sleep(5)
            
            # Check if post was published
            current_url = page.url
            page_content = page.content()
            
            if 'feed' in current_url.lower() or 'posted' in page_content.lower():
                result['status'] = 'success'
                print()
                print('✅ SUCCESS! Post published to LinkedIn!')
                print()
                print('Please check your LinkedIn profile to verify:')
                print('https://www.linkedin.com/in/your-profile')
            else:
                result['status'] = 'uncertain'
                print()
                print('⚠️ Post may or may not have been published.')
                print('Please check your LinkedIn feed manually.')
            
            # Save screenshot
            screenshot = Path(__file__).parent / 'linkedin_post_result.png'
            page.screenshot(path=str(screenshot), full_page=True)
            print(f'📸 Screenshot saved: {screenshot}')
            
            # Keep browser open for verification
            print()
            print('Browser will stay open for 10 seconds for you to verify...')
            print('Check if your post appears in the feed!')
            time.sleep(10)
            
            browser.close()
            
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
        print(f'❌ Error: {e}')
    
    return result


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Auto Poster v2')
    parser.add_argument('--email', '-e', required=True, help='LinkedIn email')
    parser.add_argument('--password', '-p', required=True, help='LinkedIn password')
    parser.add_argument('--content', '-c', required=True, help='Post content')
    
    args = parser.parse_args()
    
    result = post_to_linkedin(args.email, args.password, args.content)
    
    print()
    print('=' * 70)
    print(f'Result: {result["status"].upper()}')
    print('=' * 70)
    
    sys.exit(0 if result['status'] == 'success' else 1)


if __name__ == '__main__':
    main()
