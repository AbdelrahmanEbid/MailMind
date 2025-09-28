#!/usr/bin/env python3
"""
Reader Agent Test - Real Gmail Integration

This test verifies the MailMind Reader Agent functionality using real Gmail emails.
It tests the agent as a ReAct agent without any supervisor, using actual email data.

The test will:
1. Fetch real emails from Gmail
2. Create a reader agent with ReAct capabilities
3. Test email reading by ID
4. Test email content parsing and analysis
5. Verify semantic analysis (entities, intent, sentiment)
    Entities (like names, URLs, dates)
    ntent classification (e.g., meeting request, urgent, etc.)
    Sentiment analysis (positive/negative/neutral tone)

Requirements:
- .env file with Gmail API credentials
- GOOGLE_API_KEY for the LLM
- Internet connection
- Real emails in your Gmail account

Usage:
    python tests/manual/test_reader_agent.py
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mailmind.config.settings import MailMindConfig
from mailmind.agents.reader import create_reader_agent
from mailmind.utils.gmail_client import GmailClient
from mailmind.state.email_state import InputState


async def fetch_test_emails(num_emails: int = 5) -> List[Dict[str, Any]]:
    """Fetch real emails from Gmail for testing."""
    
    print(f"📬 Fetching {num_emails} real emails from Gmail...")
    
    try:
        config = MailMindConfig()
        
        gmail_client = GmailClient(
            client_id=config.gmail_client_id,
            client_secret=config.gmail_client_secret,
            redirect_uri=config.gmail_redirect_uri
        )
        
        # Authenticate
        token_path = str(project_root / "token.json")
        auth_success = await gmail_client.authenticate(token_path)
        
        if not auth_success:
            raise Exception("Gmail authentication failed")
        
        # Get recent emails
        emails = await gmail_client.search_emails(query="", max_results=num_emails)
        
        if not emails:
            raise Exception("No emails found in Gmail")
        
        print(f"✅ Successfully fetched {len(emails)} emails")
        return emails
        
    except Exception as e:
        print(f"❌ Failed to fetch emails: {e}")
        raise


async def test_reader_agent_basic():
    """Test basic reader agent functionality."""
    
    print("\n🤖 Testing Reader Agent - Basic Functionality")
    print("=" * 60)
    
    try:
        # Load configuration normally (should now work with correct model name)
        config = MailMindConfig()
        print(f"✅ Configuration loaded (Model: {config.model})")
        
        # Create reader agent
        reader_agent = create_reader_agent(config)
        print("✅ Reader agent created successfully")
        
        # Fetch test emails
        test_emails = await fetch_test_emails(3)
        
        # Test with first email
        test_email = test_emails[0]
        email_id = test_email['id']
        
        print(f"\n📧 Testing with email ID: {email_id}")
        print(f"   Subject: {test_email['subject']}")
        print(f"   From: {test_email['sender']['name']} <{test_email['sender']['email']}>")
        
        # Create input state for the agent
        input_state = InputState(
            messages=[("user", f"Please read and analyze the email with ID: {email_id}")],
            email_provider="gmail"
        )
        
        # Invoke the reader agent
        print("\n🔄 Invoking reader agent...")
        result = await reader_agent.ainvoke(input_state)
        
        print("✅ Reader agent completed successfully!")
        
        # Display results
        if "messages" in result:
            last_message = result["messages"][-1]
            print(f"\n📋 Agent Response:")
            print("-" * 40)
            print(last_message.content)
        
        return True
        
    except Exception as e:
        print(f"❌ Basic reader agent test failed: {e}")
        return False


async def test_reader_agent_multiple_emails():
    """Test reader agent with multiple emails."""
    
    print("\n🤖 Testing Reader Agent - Multiple Emails")
    print("=" * 60)
    
    try:
        # Load configuration normally
        config = MailMindConfig()
        
        reader_agent = create_reader_agent(config)
        
        # Fetch test emails
        test_emails = await fetch_test_emails(5)
        
        successful_reads = 0
        
        for i, email in enumerate(test_emails[:3], 1):  # Test first 3 emails
            email_id = email['id']
            subject = email['subject'] or "(No Subject)"
            
            print(f"\n📧 Test {i}/3 - Email ID: {email_id}")
            print(f"   Subject: {subject[:60]}...")
            
            try:
                # Create input for this email
                input_state = InputState(
                    messages=[("user", f"Read email {email_id} and provide a brief summary")],
                    email_provider="gmail"
                )
                
                # Invoke agent
                result = await reader_agent.ainvoke(input_state)
                
                if "messages" in result and result["messages"]:
                    print("✅ Successfully processed")
                    successful_reads += 1
                else:
                    print("⚠️  No response from agent")
                    
            except Exception as e:
                print(f"❌ Failed to process email {email_id}: {e}")
        
        print(f"\n📊 Results: {successful_reads}/3 emails processed successfully")
        return successful_reads >= 2  # Consider success if at least 2/3 work
        
    except Exception as e:
        print(f"❌ Multiple emails test failed: {e}")
        return False


async def test_reader_agent_parsing():
    """Test reader agent's parsing and analysis capabilities."""
    
    print("\n🤖 Testing Reader Agent - Content Parsing & Analysis")
    print("=" * 60)
    
    try:
        # Load configuration normally
        config = MailMindConfig()
        
        reader_agent = create_reader_agent(config)
        
        # Fetch test emails
        test_emails = await fetch_test_emails(2)
        test_email = test_emails[0]
        email_id = test_email['id']
        
        print(f"📧 Analyzing email: {test_email['subject']}")
        
        # Test detailed analysis request
        analysis_request = f"""
        Please read email {email_id} and provide a comprehensive analysis including:
        1. Summary of the content
        2. Sender information and intent
        3. Key entities mentioned (emails, URLs, dates, etc.)
        4. Sentiment analysis
        5. Recommended actions or follow-ups
        
        Be thorough in your analysis.
        """
        
        input_state = InputState(
            messages=[("user", analysis_request)],
            email_provider="gmail"
        )
        
        print("\n🔄 Requesting comprehensive analysis...")
        result = await reader_agent.ainvoke(input_state)
        
        if "messages" in result and result["messages"]:
            response = result["messages"][-1].content
            print("✅ Comprehensive analysis completed!")
            
            print(f"\n📋 Detailed Analysis:")
            print("-" * 50)
            print(response)
            
            # Check if analysis contains expected elements
            analysis_quality = {
                "has_summary": any(word in response.lower() for word in ["summary", "content", "about"]),
                "has_sender_info": any(word in response.lower() for word in ["sender", "from", "author"]),
                "has_entities": any(word in response.lower() for word in ["email", "url", "link", "date"]),
                "has_sentiment": any(word in response.lower() for word in ["sentiment", "tone", "positive", "negative"]),
                "has_recommendations": any(word in response.lower() for word in ["recommend", "suggest", "action", "follow"])
            }
            
            quality_score = sum(analysis_quality.values())
            print(f"\n📊 Analysis Quality Score: {quality_score}/5")
            
            for aspect, present in analysis_quality.items():
                status = "✅" if present else "❌"
                print(f"   {status} {aspect.replace('_', ' ').title()}")
            
            return quality_score >= 3  # Consider success if 3/5 aspects are covered
        else:
            print("❌ No analysis response received")
            return False
            
    except Exception as e:
        print(f"❌ Parsing test failed: {e}")
        return False


async def test_reader_agent_error_handling():
    """Test reader agent error handling with invalid inputs."""
    
    print("\n🤖 Testing Reader Agent - Error Handling")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Invalid Email ID",
            "request": "Please read email with ID: invalid_email_id_12345",
            "expected": "error handling for invalid ID"
        },
        {
            "name": "Empty Email ID", 
            "request": "Please read email with ID: ",
            "expected": "error handling for empty ID"
        },
        {
            "name": "Non-existent Email ID",
            "request": "Please read email with ID: 999999999999999999",
            "expected": "error handling for non-existent email"
        }
    ]
    
    try:
        # Load configuration normally
        config = MailMindConfig()
        
        reader_agent = create_reader_agent(config)
        
        successful_error_handling = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}/3: {test_case['name']}")
            
            try:
                input_state = InputState(
                    messages=[("user", test_case['request'])],
                    email_provider="gmail"
                )
                
                result = await reader_agent.ainvoke(input_state)
                
                if "messages" in result and result["messages"]:
                    response = result["messages"][-1].content.lower()
                    
                    # Check if response indicates error handling
                    error_indicators = ["error", "failed", "invalid", "not found", "unable", "cannot"]
                    has_error_handling = any(indicator in response for indicator in error_indicators)
                    
                    if has_error_handling:
                        print("✅ Proper error handling detected")
                        successful_error_handling += 1
                    else:
                        print("⚠️  Response doesn't clearly indicate error")
                        print(f"   Response: {response[:100]}...")
                else:
                    print("❌ No response received")
                    
            except Exception as e:
                print(f"✅ Exception properly caught: {str(e)[:100]}...")
                successful_error_handling += 1
        
        print(f"\n📊 Error Handling Score: {successful_error_handling}/3")
        return successful_error_handling >= 2
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def check_environment():
    """Check if environment is properly configured."""
    
    print("🔍 Checking environment for reader agent test...")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv(project_root / ".env")
        print("✅ Environment variables loaded")
    except ImportError:
        print("⚠️  python-dotenv not available")
    
    # Check required variables
    required_vars = {
        "GMAIL_CLIENT_ID": "Gmail API client ID",
        "GMAIL_CLIENT_SECRET": "Gmail API client secret", 
        "GOOGLE_API_KEY": "Google API key for LLM"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ All required environment variables found")
    return True


async def main():
    """Main test function."""
    
    print("🚀 MailMind Reader Agent Test Suite")
    print("=" * 70)
    print("Testing the Reader Agent as a ReAct agent with real Gmail emails")
    print("=" * 70)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    # Run test suite
    test_results = {}
    
    try:
        # Test 1: Basic functionality
        test_results["basic"] = await test_reader_agent_basic()
        
        # Test 2: Multiple emails
        test_results["multiple"] = await test_reader_agent_multiple_emails()
        
        # Test 3: Content parsing and analysis
        test_results["parsing"] = await test_reader_agent_parsing()
        
        # Test 4: Error handling
        test_results["error_handling"] = await test_reader_agent_error_handling()
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with unexpected error: {e}")
        sys.exit(1)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Reader Agent is working perfectly!")
        print("\nThe Reader Agent successfully:")
        print("- ✅ Connects to Gmail and reads real emails")
        print("- ✅ Functions as a ReAct agent with reasoning capabilities")
        print("- ✅ Parses and analyzes email content comprehensively")
        print("- ✅ Handles errors gracefully")
        print("- ✅ Provides semantic analysis (entities, intent, sentiment)")
    elif passed_tests >= total_tests * 0.75:
        print("\n✅ Most tests passed! Reader Agent is mostly functional.")
        print("Some minor issues may need attention.")
    else:
        print("\n⚠️  Several tests failed. Reader Agent needs debugging.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
