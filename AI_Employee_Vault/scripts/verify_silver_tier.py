"""
Silver Tier Verification Script

Tests all Silver Tier components:
- Gmail Watcher
- LinkedIn Watcher
- LinkedIn Poster
- Orchestrator
- Plan Creator

Usage:
    python verify_silver_tier.py
"""

import sys
import io
import json
from pathlib import Path

# Fix Windows console encoding for Unicode emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_import(name, install_cmd):
    """Check if a module can be imported"""
    try:
        __import__(name)
        print(f'✅ {name}: OK')
        return True
    except ImportError as e:
        print(f'❌ {name}: Not installed - Run: {install_cmd}')
        return False

def check_file(path, description):
    """Check if a file exists"""
    if path.exists():
        print(f'✅ {description}: Found')
        return True
    else:
        print(f'❌ {description}: Not found - {path}')
        return False

def check_credentials():
    """Check for Gmail credentials"""
    possible_paths = [
        Path.cwd() / 'credentials.json',
        Path(__file__).parent.parent / 'credentials.json',
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f'✅ Gmail credentials: Found at {path}')
            return True
    
    print('❌ Gmail credentials: Not found')
    print('   Please create credentials.json from Google Cloud Console')
    print('   Place it in the project root directory')
    return False

def main():
    print('=' * 60)
    print('Silver Tier Verification')
    print('=' * 60)
    print()
    
    # Check Python dependencies
    print('📦 Python Dependencies:')
    print('-' * 40)
    deps_ok = True
    deps_ok &= check_import('watchdog', 'pip install watchdog')
    deps_ok &= check_import('playwright', 'pip install playwright && playwright install')
    deps_ok &= check_import('google.oauth2.credentials', 'pip install google-auth google-auth-oauthlib google-api-python-client')
    print()
    
    # Check watcher scripts
    print('📜 Watcher Scripts:')
    print('-' * 40)
    scripts_dir = Path(__file__).parent
    scripts_ok = True
    scripts_ok &= check_file(scripts_dir / 'base_watcher.py', 'base_watcher.py')
    scripts_ok &= check_file(scripts_dir / 'filesystem_watcher.py', 'filesystem_watcher.py')
    scripts_ok &= check_file(scripts_dir / 'gmail_watcher.py', 'gmail_watcher.py')
    scripts_ok &= check_file(scripts_dir / 'linkedin_watcher.py', 'linkedin_watcher.py')
    scripts_ok &= check_file(scripts_dir / 'orchestrator.py', 'orchestrator.py')
    print()
    
    # Check skills
    print('🛠️ Qwen Code Skills:')
    print('-' * 40)
    # Skills are in the root project directory
    skills_dir = Path(__file__).parent.parent.parent / '.qwen' / 'skills'
    skills_ok = True
    skills_ok &= check_file(skills_dir / 'email-sender' / 'SKILL.md', 'email-sender skill')
    skills_ok &= check_file(skills_dir / 'approval-workflow' / 'SKILL.md', 'approval-workflow skill')
    skills_ok &= check_file(skills_dir / 'scheduler' / 'SKILL.md', 'scheduler skill')
    skills_ok &= check_file(skills_dir / 'plan-creator' / 'SKILL.md', 'plan-creator skill')
    skills_ok &= check_file(skills_dir / 'linkedin-poster' / 'SKILL.md', 'linkedin-poster skill')
    skills_ok &= check_file(skills_dir / 'browsing-with-playwright' / 'SKILL.md', 'browsing-with-playwright skill')
    print()
    
    # Check vault structure
    print('📁 Vault Structure:')
    print('-' * 40)
    vault_dir = scripts_dir.parent
    vault_ok = True
    vault_ok &= check_file(vault_dir / 'Dashboard.md', 'Dashboard.md')
    vault_ok &= check_file(vault_dir / 'Company_Handbook.md', 'Company_Handbook.md')
    vault_ok &= check_file(vault_dir / 'Business_Goals.md', 'Business_Goals.md')
    vault_ok &= check_file(vault_dir / 'Needs_Action', 'Needs_Action folder')
    vault_ok &= check_file(vault_dir / 'Plans', 'Plans folder')
    vault_ok &= check_file(vault_dir / 'Done', 'Done folder')
    vault_ok &= check_file(vault_dir / 'Pending_Approval', 'Pending_Approval folder')
    vault_ok &= check_file(vault_dir / 'Approved', 'Approved folder')
    print()
    
    # Check credentials
    print('🔐 Credentials:')
    print('-' * 40)
    check_credentials()
    print()
    
    # Check Playwright browsers
    print('🌐 Playwright Browsers:')
    print('-' * 40)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            if p.chromium:
                print('✅ Chromium browser: Available')
            else:
                print('❌ Chromium browser: Not installed - Run: playwright install chromium')
    except Exception as e:
        print(f'❌ Playwright check failed: {e}')
    print()
    
    # Summary
    print('=' * 60)
    print('Summary')
    print('=' * 60)
    
    all_ok = deps_ok and scripts_ok and skills_ok and vault_ok
    
    if all_ok:
        print('✅ All Silver Tier components are ready!')
        print()
        print('Next steps:')
        print('1. Ensure credentials.json is configured for Gmail API')
        print('2. Run Gmail authentication: python gmail_watcher.py "../" --once')
        print('3. Run LinkedIn login: python linkedin_watcher.py "../" --login')
        print('4. Start watchers: python filesystem_watcher.py "../" "../DropFolder"')
        print('5. Process items: python orchestrator.py "../"')
    else:
        print('⚠️ Some components are missing. Please install/configure them.')
        print()
        print('Install dependencies:')
        print('  pip install -r requirements.txt')
        print()
        print('Install Playwright browsers:')
        print('  playwright install chromium')
    
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
