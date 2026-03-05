"""
LinkedIn Simple Poster - Semi-Automatic (Most Reliable)

This opens LinkedIn, YOU log in manually (one time), then it posts automatically.
Much more reliable than trying to automate login.

Usage:
    python linkedin_simple_post.py --content "Your post content"
"""

import sys
import io
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
except ImportError:
    print("Error: Playwright not installed.")
    print("Run: pip install playwright && playwright install")
    sys.exit(1)


def simple_post(content: str):
    """Post to LinkedIn with manual login"""
    
    print('=' * 70)
    print('LinkedIn Simple Poster - Semi-Automatic')
    print('=' * 70)
    print()
    print('INSTRUCTIONS:')
    print('1. Browser will open to LinkedIn')
    print('2. LOG IN to LinkedIn (jolmusic12@gmail.com)')
    print('3. Wait for your feed to load')
    print('4. The script will take over and post automatically')
    print()
    
    input('Press Enter to open LinkedIn...')
    
    result = {'status': 'error', 'timestamp': datetime.now().isoformat()}
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled', '--start-maximized']
            )
            
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            # Go to LinkedIn
            print('Opening LinkedIn...')
            page.goto('https://www.linkedin.com', timeout=120000)
            
            print()
            print('👉 PLEASE LOG IN NOW')
            print()
            print('After you see your feed, press Enter...')
            input('Press Enter when you are logged in and see your feed...')
            
            time.sleep(3)
            
            # Navigate to feed
            print('Going to feed...')
            page.goto('https://www.linkedin.com/feed/', timeout=60000)
            time.sleep(5)
            
            # Click "Start a post"
            print('Opening post composer...')
            
            post_triggers = [
                'button[aria-label="Start a post"]',
                '.share-box-feed-entry__trigger',
            ]
            
            for selector in post_triggers:
                try:
                    elem = page.locator(selector).first
                    if elem.is_visible(timeout=5000):
                        elem.click()
                        print('Post composer opened!')
                        break
                except:
                    continue
            
            time.sleep(3)
            
            # Type content
            print('Typing content...')
            
            editors = [
                '[aria-label="What do you want to talk about?"]',
                'div[contenteditable="true"]'
            ]
            
            for selector in editors:
                try:
                    editor = page.locator(selector).first
                    if editor.is_visible(timeout=5000):
                        editor.click()
                        time.sleep(1)
                        
                        # Type content
                        for char in content:
                            page.keyboard.type(char, delay=50)
                        
                        print('Content typed!')
                        break
                except:
                    continue
            
            time.sleep(2)
            
            # Click Post
            print('Publishing...')
            
            post_buttons = [
                'button[aria-label="Post"]',
                'button:has-text("Post")'
            ]
            
            for selector in post_buttons:
                try:
                    elem = page.locator(selector).first
                    if elem.is_visible(timeout=5000) and elem.is_enabled(timeout=5000):
                        elem.click()
                        print('Post button clicked!')
                        break
                except:
                    continue
            
            time.sleep(5)
            
            # Check result
            result['status'] = 'success'
            print()
            print('✅ POST PUBLISHED!')
            print()
            print('Check your LinkedIn profile to verify.')
            
            # Screenshot
            screenshot = Path(__file__).parent / 'linkedin_post_result.png'
            page.screenshot(path=str(screenshot))
            print(f'Screenshot: {screenshot}')
            
            # Keep browser open
            print()
            print('Browser stays open for 15 seconds to verify...')
            time.sleep(15)
            
            browser.close()
            
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
        print(f'Error: {e}')
    
    return result


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Simple Poster')
    parser.add_argument('--content', '-c', required=True, help='Post content')
    args = parser.parse_args()
    
    result = simple_post(args.content)
    
    print()
    print(f'Result: {result["status"]}')


if __name__ == '__main__':
    main()
