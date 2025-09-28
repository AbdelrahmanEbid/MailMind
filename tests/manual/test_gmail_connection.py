#!/usr/bin/env python3
"""
Manual test for Gmail connection functionality.

This test verifies that the Gmail API connection is working properly
and can retrieve the 10 most recent emails from the inbox.

Requirements:
1. A .env file with proper Gmail API credentials
2. OAuth token.json file (will be created during first run)
3. Internet connection

Usage:
    python tests/manual/test_gmail_connection.py
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the src directory to the path so we can import mailmind modules
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from mailmind.config.settings import MailMindConfig
from mailmind.utils.gmail_client import GmailClient


async def test_gmail_connection():
    """Test Gmail API connection and email retrieval."""
    
    print("🔧 MailMind Gmail Connection Test")
    print("=" * 50)
    
    # Load configuration
    try:
        config = MailMindConfig()
        print("✅ Configuration loaded successfully")
        
        # Validate Gmail credentials
        if not config.gmail_client_id or not config.gmail_client_secret:
            print("❌ Missing Gmail API credentials!")
            print("Please ensure GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET are set in your .env file")
            return False
            
        print(f"📧 Email Provider: {config.email_provider}")
        print(f"🔑 Client ID: {config.gmail_client_id[:20]}...")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Initialize Gmail client
    try:
        gmail_client = GmailClient(
            client_id=config.gmail_client_id,
            client_secret=config.gmail_client_secret,
            redirect_uri=config.gmail_redirect_uri
        )
        print("✅ Gmail client initialized")
        
    except Exception as e:
        print(f"❌ Failed to initialize Gmail client: {e}")
        return False
    
    # Authenticate with Gmail API
    print("\n🔐 Authenticating with Gmail API...")
    try:
        token_file = project_root / "token.json"
        success = await gmail_client.authenticate(str(token_file))
        
        if not success:
            print("❌ Gmail authentication failed!")
            return False
            
        print("✅ Gmail authentication successful")
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Test email search - get 10 most recent emails
    print("\n📬 Retrieving 10 most recent emails...")
    try:
        # Search for recent emails (empty query gets all emails)
        emails = await gmail_client.search_emails(
            query="",  # Empty query to get all emails
            max_results=10
        )
        
        if not emails:
            print("⚠️  No emails found in inbox")
            return True
        
        print(f"✅ Successfully retrieved {len(emails)} emails")
        
        # Display email details
        print("\n📋 Email Summary:")
        print("-" * 80)
        
        for i, email in enumerate(emails, 1):
            sender_name = email['sender']['name'] or email['sender']['email']
            subject = email['subject'] or "(No Subject)"
            timestamp = email['timestamp']
            is_read = "✅" if email['is_read'] else "🔴"
            
            print(f"{i:2d}. {is_read} From: {sender_name}")
            print(f"     Subject: {subject}")
            print(f"     Date: {timestamp}")
            print(f"     ID: {email['id']}")
            
            # Show a snippet of the body if available
            if email['body']['text']:
                snippet = email['body']['text'][:100].replace('\n', ' ').strip()
                if len(email['body']['text']) > 100:
                    snippet += "..."
                print(f"     Preview: {snippet}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to retrieve emails: {e}")
        return False


async def test_specific_email_retrieval():
    """Test retrieving a specific email by ID."""
    
    print("\n🎯 Testing specific email retrieval...")
    
    try:
        config = MailMindConfig()
        gmail_client = GmailClient(
            client_id=config.gmail_client_id,
            client_secret=config.gmail_client_secret,
            redirect_uri=config.gmail_redirect_uri
        )
        
        token_file = Path(__file__).parent.parent.parent / "token.json"
        await gmail_client.authenticate(str(token_file))
        
        # Get the first email from our recent search
        emails = await gmail_client.search_emails("", max_results=1)
        
        if not emails:
            print("⚠️  No emails available for specific retrieval test")
            return True
        
        email_id = emails[0]['id']
        print(f"📧 Retrieving email with ID: {email_id}")
        
        # Get the specific email
        specific_email = await gmail_client.get_email(email_id)
        
        print("✅ Successfully retrieved specific email")
        print(f"   Subject: {specific_email['subject']}")
        print(f"   From: {specific_email['sender']['name']} <{specific_email['sender']['email']}>")
        print(f"   Labels: {', '.join(specific_email['labels'])}")
        
        if specific_email['attachments']:
            print(f"   Attachments: {len(specific_email['attachments'])} files")
            for att in specific_email['attachments']:
                print(f"     - {att['filename']} ({att['mime_type']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Specific email retrieval failed: {e}")
        return False


def check_environment():
    """Check if the environment is properly set up."""
    
    print("🔍 Checking environment setup...")
    
    # Check if .env file exists
    env_file = Path(__file__).parent.parent.parent / ".env"
    if not env_file.exists():
        print("⚠️  .env file not found. Please create one based on env.example")
        return False
    
    # Load environment variables from .env file first
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print("✅ Environment variables loaded from .env")
    except ImportError:
        print("⚠️  python-dotenv not installed. Trying without it...")
    except Exception as e:
        print(f"⚠️  Could not load .env file: {e}")
    
    # Check required environment variables (only Gmail credentials for this test)
    required_vars = [
        "GMAIL_CLIENT_ID", 
        "GMAIL_CLIENT_SECRET"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return False
    
    # Optional: Check for GOOGLE_API_KEY (not required for Gmail connection test)
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  GOOGLE_API_KEY not found (optional for Gmail connection test)")
    
    print("✅ Environment setup looks good")
    return True


async def main():
    """Main test function."""
    
    print("🚀 Starting MailMind Gmail Connection Test")
    print("=" * 60)
    
    # Check environment first
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    # Environment variables are loaded in check_environment()
    
    # Run the main Gmail connection test
    success1 = await test_gmail_connection()
    
    if success1:
        # Run the specific email retrieval test
        success2 = await test_specific_email_retrieval()
        
        if success1 and success2:
            print("\n🎉 All tests passed! Gmail connection is working properly.")
            print("\nNext steps:")
            print("- Your Gmail API connection is verified")
            print("- You can now use the MailMind agents to process emails")
            print("- Check the examples/ directory for usage patterns")
        else:
            print("\n⚠️  Some tests failed, but basic connection works.")
    else:
        print("\n❌ Gmail connection test failed. Please check your configuration.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
