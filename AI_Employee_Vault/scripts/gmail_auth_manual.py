"""
Gmail Manual Authentication - Copy-paste flow

This script helps you authenticate with Gmail API using a copy-paste flow
instead of relying on localhost redirect.

Usage:
    python gmail_auth_manual.py
"""

import sys
import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow


def authenticate_gmail_manual():
    """Authenticate with Gmail using manual copy-paste flow"""
    
    # Find credentials
    possible_paths = [
        Path(__file__).parent / 'credentials.json',
        Path(__file__).parent.parent / 'credentials.json',
        Path(__file__).parent.parent.parent / 'credentials.json',
    ]
    
    credentials_path = None
    for p in possible_paths:
        if p.exists():
            credentials_path = p
            break
    
    if not credentials_path:
        print("ERROR: credentials.json not found!")
        print("Please place it in the scripts folder or project root.")
        sys.exit(1)
    
    print("=" * 60)
    print("Gmail API Authentication (Manual)")
    print("=" * 60)
    print()
    print("Using credentials: " + str(credentials_path))
    print()
    
    scopes = ['https://www.googleapis.com/auth/gmail.readonly']
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, scopes
        )
        
        # Use run_local_server with open_browser=False
        # User copies URL manually if browser doesn't open
        print("Starting authentication...")
        print()
        print("A browser window should open automatically.")
        print("If not, copy the URL that appears below and paste it in your browser.")
        print()
        
        creds = flow.run_local_server(port=0, open_browser=True)
        
        # Save token
        token_path = Path(__file__).parent / 'token.json'
        token_path.write_text(creds.to_json())
        
        print()
        print("=" * 60)
        print("SUCCESS: Authentication successful!")
        print("=" * 60)
        print()
        print("Token saved to: " + str(token_path))
        print()
        print("You can now use gmail_watcher.py")
        
    except Exception as e:
        print()
        print("=" * 60)
        print("Authentication failed: " + str(e))
        print("=" * 60)


if __name__ == '__main__':
    authenticate_gmail_manual()
