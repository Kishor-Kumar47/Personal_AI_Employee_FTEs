"""
LinkedIn Manual Poster - Open Browser and Post

This simply opens LinkedIn in a browser. You:
1. Log in manually
2. The script helps you post

Usage:
    python linkedin_manual.py
"""

import sys
import io
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed. Run: pip install playwright && playwright install")
    sys.exit(1)


print('=' * 70)
print('LinkedIn Manual Poster')
print('=' * 70)
print()
print('Opening LinkedIn in a browser window...')
print()
print('WHAT TO DO:')
print('1. Log in to LinkedIn (jolmusic12@gmail.com)')
print('2. Click "Start a post"')
print('3. Type or paste your post')
print('4. Click "Post"')
print()
print('The browser will stay open for 2 minutes.')
print()

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=['--start-maximized']
    )
    
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080}
    )
    
    page = context.new_page()
    
    # Go to LinkedIn
    print('Loading LinkedIn...')
    page.goto('https://www.linkedin.com', timeout=120000)
    
    print()
    print('✅ LinkedIn is open!')
    print()
    print('Browser will stay open for 2 minutes.')
    print('Use this time to:')
    print('  - Log in')
    print('  - Create and publish your post')
    print()
    
    # Wait 2 minutes
    for i in range(120, 0, -1):
        time.sleep(1)
        if i % 10 == 0:
            print(f'   {i} seconds remaining...')
    
    browser.close()
    print()
    print('Browser closed.')
