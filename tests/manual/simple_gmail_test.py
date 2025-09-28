#!/usr/bin/env python3
"""
Simple Gmail Connection Test

This is a straightforward test to verify Gmail API connection
and retrieve the 10 most recent emails from your inbox.

⚠️ Note:
By default, this test fetches the 10 most recent emails from your
**entire mailbox** (Gmail API uses the "All Mail" label by default),
not just the "Inbox". 
So you might see emails that do not appear in your Inbox tab.
To confirm, open Gmail in the browser and switch to **All Mail**
to view the fetched messages.

Setup:
1. Create .env file with your Gmail API credentials
2. Run: python tests/manual/simple_gmail_test.py
3. Follow OAuth flow in browser (first time only)

Requirements in .env:
- GMAIL_CLIENT_ID=your_gmail_client_id
- GMAIL_CLIENT_SECRET=your_gmail_client_secret
- GOOGLE_API_KEY=your_google_api_key (optional for this test)
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mailmind.utils.gmail_client import GmailClient


async def main():
    """Simple test to connect to Gmail and get 10 recent emails."""
    
    print("📧 Simple Gmail Connection Test")
    print("=" * 40)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv(project_root / ".env")
    except ImportError:
        print("⚠️  Install python-dotenv: pip install python-dotenv")
    
    # Get credentials from environment
    client_id = os.getenv("GMAIL_CLIENT_ID")
    client_secret = os.getenv("GMAIL_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ Missing Gmail credentials!")
        print("Please set GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET in .env file")
        return
    
    print(f"✅ Using Client ID: {client_id[:20]}...")
    
    # Initialize Gmail client
    gmail = GmailClient(
        client_id=client_id,
        client_secret=client_secret
    )
    
    # Authenticate
    print("\n🔐 Authenticating with Gmail...")
    token_path = str(project_root / "token.json")
    
    auth_success = await gmail.authenticate(token_path)
    if not auth_success:
        print("❌ Authentication failed!")
        return
    
    print("✅ Authentication successful!")
    
    # Get 10 recent emails
    print("\n📬 Fetching 10 most recent emails...")
    try:
        emails = await gmail.search_emails(query="", max_results=10)
        
        if not emails:
            print("⚠️  No emails found")
            return
        
        print(f"✅ Retrieved {len(emails)} emails\n")
        
        # Display emails
        for i, email in enumerate(emails, 1):
            sender = email['sender']['name'] or email['sender']['email']
            subject = email['subject'] or "(No Subject)"
            read_status = "✅ Read" if email['is_read'] else "🔴 Unread"
            
            print(f"{i:2d}. {read_status}")
            print(f"    From: {sender}")
            print(f"    Subject: {subject}")
            print(f"    Date: {email['timestamp']}")
            
            # Show preview of body
            body = email['body']['text'] or email['body']['html']
            if body:
                preview = body[:80].replace('\n', ' ').strip()
                if len(body) > 80:
                    preview += "..."
                print(f"    Preview: {preview}")
            
            print()
        
        print("🎉 Gmail connection test completed successfully!")
        print("\nYour Gmail API is working correctly.")
        print("You can now use this connection in the MailMind agents.")
        
    except Exception as e:
        print(f"❌ Error retrieving emails: {e}")


if __name__ == "__main__":
    asyncio.run(main())
