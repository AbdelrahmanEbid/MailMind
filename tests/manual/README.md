# Manual Tests

This directory contains manual tests for verifying MailMind functionality without mocking.

## Gmail Connection Tests

### Prerequisites

1. **Gmail API Setup**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project or select existing one
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop Application)
   - Download credentials or note Client ID and Secret

2. **Environment Configuration**:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add:
   ```
   GMAIL_CLIENT_ID=your_gmail_client_id
   GMAIL_CLIENT_SECRET=your_gmail_client_secret
   GOOGLE_API_KEY=your_google_api_key  # Optional for connection test
   ```

3. **Dependencies**:
   ```bash
   pip install python-dotenv  # If not already installed
   ```

## Available Tests

### 1. Simple Gmail Test (`simple_gmail_test.py`)

**Purpose**: Basic Gmail connection and retrieve 10 recent emails

**Usage**:
```bash
cd /path/to/MailMind
python tests/manual/simple_gmail_test.py
```

**What it does**:
- ✅ Loads Gmail API credentials
- ✅ Authenticates via OAuth (opens browser first time)
- ✅ Retrieves 10 most recent emails
- ✅ Displays email summary (sender, subject, date, read status)

### 2. Comprehensive Gmail Test (`test_gmail_connection.py`)

**Purpose**: Thorough Gmail API testing with detailed diagnostics

**Usage**:
```bash
cd /path/to/MailMind
python tests/manual/test_gmail_connection.py
```

**What it does**:
- ✅ Environment validation
- ✅ Configuration loading
- ✅ Gmail authentication
- ✅ Email search and retrieval
- ✅ Specific email fetching by ID
- ✅ Attachment detection
- ✅ Detailed error reporting

### Key Differences Between Both Tests:

| Feature | Simple Test | Comprehensive Test |
|---------|-------------|-------------------|
| **Purpose** | Quick Gmail connection check | Thorough Gmail API testing |
| **Environment Loading** | ✅ Uses `python-dotenv` | ✅ Now fixed - uses `python-dotenv` |
| **Required Variables** | Only Gmail credentials | Only Gmail credentials (fixed) |
| **Email Retrieval** | Basic list of 10 emails | ✅ + Specific email by ID |
| **Additional Features** | Email preview | ✅ + Attachment detection |
| **Error Reporting** | Simple | ✅ Detailed diagnostics |
| **OAuth Testing** | Basic | ✅ Comprehensive |

## First Time Setup

1. **Run the simple test first**:
   ```bash
   python tests/manual/simple_gmail_test.py
   ```

2. **OAuth Flow**:
   - Browser will open automatically
   - Sign in to your Google account
   - Grant permissions to the app
   - `token.json` will be created automatically

3. **Verify Results**:
   - You should see your 10 most recent emails
   - Check that authentication works
   - Verify email data is parsed correctly

## Troubleshooting

### Common Issues

1. **"Missing Gmail credentials"**:
   - Check your `.env` file exists
   - Verify `GMAIL_CLIENT_ID` and `GMAIL_CLIENT_SECRET` are set
   - Ensure no extra spaces or quotes

2. **"Authentication failed"**:
   - Delete `token.json` and try again
   - Check Gmail API is enabled in Google Cloud Console
   - Verify OAuth consent screen is configured

3. **"No emails found"**:
   - Check your Gmail inbox has emails
   - Verify you're using the correct Google account
   - Try with a different search query

4. **Import errors**:
   - Run from project root directory
   - Install missing dependencies: `pip install -e .`

### Debug Mode

Add debug logging to see detailed API calls:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Expected Output

Successful test should show:
```
📧 Simple Gmail Connection Test
========================================
✅ Using Client ID: 123456789...
🔐 Authenticating with Gmail...
✅ Authentication successful!
📬 Fetching 10 most recent emails...
✅ Retrieved 10 emails

 1. ✅ Read
    From: John Doe
    Subject: Meeting Tomorrow
    Date: Mon, 01 Jan 2024 10:00:00 +0000
    Preview: Hi, just wanted to confirm our meeting tomorrow at 2pm...

...

🎉 Gmail connection test completed successfully!
```

## Next Steps

Once these tests pass:
1. Your Gmail API connection is verified
2. You can run the full MailMind agents
3. Try the examples in `examples/` directory
4. Use LangGraph Studio for interactive testing
