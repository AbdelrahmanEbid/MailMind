"""Gmail API client for MailMind."""

from __future__ import annotations

import base64
import logging
import os
from typing import Any, Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]


class GmailClient:
    """Gmail API client for email operations."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str = "http://localhost:8080/callback"
    ):
        """Initialize Gmail client.
        
        Args:
            client_id: OAuth client ID from Google Cloud Console
            client_secret: OAuth client secret from Google Cloud Console
            redirect_uri: OAuth redirect URI
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.service = None
        self.credentials = None
        
    async def authenticate(self, token_file: str = "token.json") -> bool:
        """Authenticate with Gmail API.
        
        Args:
            token_file: Path to store/load OAuth token
            
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Load existing credentials
            if os.path.exists(token_file):
                self.credentials = Credentials.from_authorized_user_file(token_file, SCOPES)
            
            # If credentials are invalid or don't exist, get new ones
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    logger.info("Refreshing expired credentials")
                    self.credentials.refresh(Request())
                else:
                    logger.info("Starting OAuth flow for new credentials")
                    
                    # Create client config
                    client_config = {
                        "web": {
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": [self.redirect_uri]
                        }
                    }
                    
                    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                    self.credentials = flow.run_local_server(port=8080)
                
                # Save credentials for next time
                with open(token_file, 'w') as token:
                    token.write(self.credentials.to_json())
                    
            # Build the service
            self.service = build('gmail', 'v1', credentials=self.credentials)
            logger.info("Gmail API authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Gmail authentication failed: {e}")
            return False
    
    async def get_email(self, email_id: str) -> Dict[str, Any]:
        """Get email by ID.
        
        Args:
            email_id: Gmail message ID
            
        Returns:
            Dictionary containing email data
        """
        if not self.service:
            raise RuntimeError("Gmail client not authenticated. Call authenticate() first.")
        
        try:
            # Get the message
            message = self.service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()
            
            # Parse the message
            parsed_email = self._parse_message(message)
            logger.info(f"Successfully retrieved email {email_id}")
            return parsed_email
            
        except HttpError as e:
            logger.error(f"Failed to get email {email_id}: {e}")
            raise
    
    async def search_emails(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search emails using Gmail query syntax.
        
        Args:
            query: Gmail search query
            max_results: Maximum number of results
            
        Returns:
            List of email dictionaries
        """
        if not self.service:
            raise RuntimeError("Gmail client not authenticated. Call authenticate() first.")
        
        try:
            # Search for messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Get full details for each message
            emails = []
            for message in messages:
                try:
                    full_message = self.service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()
                    
                    parsed_email = self._parse_message(full_message)
                    emails.append(parsed_email)
                    
                except Exception as e:
                    logger.warning(f"Failed to get details for message {message['id']}: {e}")
                    continue
            
            logger.info(f"Successfully searched emails: {len(emails)} results")
            return emails
            
        except HttpError as e:
            logger.error(f"Email search failed: {e}")
            raise
    
    def _parse_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gmail API message format to our standard format.
        
        Args:
            message: Raw Gmail API message
            
        Returns:
            Parsed email dictionary
        """
        headers = {}
        payload = message.get('payload', {})
        
        # Extract headers
        for header in payload.get('headers', []):
            headers[header['name'].lower()] = header['value']
        
        # Extract body content
        body_data = self._extract_body(payload)
        
        # Parse attachments
        attachments = self._extract_attachments(payload)
        
        return {
            "id": message['id'],
            "thread_id": message.get('threadId'),
            "subject": headers.get('subject', ''),
            "sender": {
                "email": self._extract_email(headers.get('from', '')),
                "name": self._extract_name(headers.get('from', ''))
            },
            "recipient": {
                "email": self._extract_email(headers.get('to', '')),
                "name": self._extract_name(headers.get('to', ''))
            },
            "body": body_data,
            "timestamp": headers.get('date', ''),
            "attachments": attachments,
            "labels": message.get('labelIds', []),
            "is_read": 'UNREAD' not in message.get('labelIds', []),
            "is_important": 'IMPORTANT' in message.get('labelIds', []),
            "raw_headers": headers
        }
    
    def _extract_body(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """Extract email body content.
        
        Args:
            payload: Gmail message payload
            
        Returns:
            Dictionary with text and html content
        """
        body = {"text": "", "html": ""}
        
        def extract_parts(part):
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data')
                if data:
                    body['text'] = base64.urlsafe_b64decode(data).decode('utf-8')
            elif part.get('mimeType') == 'text/html':
                data = part.get('body', {}).get('data')
                if data:
                    body['html'] = base64.urlsafe_b64decode(data).decode('utf-8')
            elif 'parts' in part:
                for subpart in part['parts']:
                    extract_parts(subpart)
        
        if 'parts' in payload:
            for part in payload['parts']:
                extract_parts(part)
        else:
            extract_parts(payload)
        
        return body
    
    def _extract_attachments(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract attachment information.
        
        Args:
            payload: Gmail message payload
            
        Returns:
            List of attachment dictionaries
        """
        attachments = []
        
        def extract_attachment_parts(part):
            if part.get('filename'):
                attachments.append({
                    "filename": part['filename'],
                    "mime_type": part.get('mimeType'),
                    "size": part.get('body', {}).get('size', 0),
                    "attachment_id": part.get('body', {}).get('attachmentId')
                })
            elif 'parts' in part:
                for subpart in part['parts']:
                    extract_attachment_parts(subpart)
        
        if 'parts' in payload:
            for part in payload['parts']:
                extract_attachment_parts(part)
        
        return attachments
    
    def _extract_email(self, from_field: str) -> str:
        """Extract email address from 'From' field.
        
        Args:
            from_field: Email from field (e.g., "John Doe <john@example.com>")
            
        Returns:
            Email address
        """
        if '<' in from_field and '>' in from_field:
            return from_field.split('<')[1].split('>')[0]
        return from_field.strip()
    
    def _extract_name(self, from_field: str) -> str:
        """Extract name from 'From' field.
        
        Args:
            from_field: Email from field (e.g., "John Doe <john@example.com>")
            
        Returns:
            Sender name
        """
        if '<' in from_field:
            return from_field.split('<')[0].strip().strip('"')
        return ""
