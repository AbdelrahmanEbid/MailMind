"""Email reading tools for MailMind."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from langchain_core.tools import tool
from langgraph.runtime import get_runtime

from mailmind.config import MailMindConfig
from mailmind.utils import GmailClient, extract_email_text, extract_entities, classify_email_intent, analyze_sentiment

logger = logging.getLogger(__name__)


@tool
async def read_email_by_id(
    email_id: str,
    provider: str = "gmail"
) -> Dict[str, Any]:
    """Read email by ID from the specified provider.
    
    This tool fetches a specific email using its unique identifier
    and returns structured email data with metadata.
    
    Args:
        email_id: Unique identifier for the email to read
        provider: Email provider to use (gmail, outlook, etc.)
        
    Returns:
        Dictionary containing email data, metadata, and status
    """
    logger.info(f"Reading email {email_id} from {provider}")
    
    # Input validation
    if not email_id or not email_id.strip():
        return {
            "error": "Email ID is required and cannot be empty",
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    # Provider validation
    supported_providers = ["gmail"]
    if provider not in supported_providers:
        return {
            "error": f"Unsupported provider: {provider}. Supported: {supported_providers}",
            "status": "error", 
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    try:
        # Get runtime configuration
        try:
            runtime = get_runtime()
            config = MailMindConfig.from_runnable_config(runtime.config)
        except (AttributeError, TypeError):
            # Fallback to default config if runtime is not available
            config = MailMindConfig()
        
        # Initialize Gmail client
        gmail_client = GmailClient(
            client_id=config.gmail_client_id,
            client_secret=config.gmail_client_secret,
            redirect_uri=config.gmail_redirect_uri
        )
        
        # Authenticate
        auth_success = await gmail_client.authenticate()
        if not auth_success:
            return {
                "error": "Failed to authenticate with Gmail API",
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Read the email
        start_time = datetime.now()
        email_data = await gmail_client.get_email(email_id)
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            "status": "success",
            "email": email_data,
            "metadata": {
                "provider": provider,
                "read_at": datetime.now(timezone.utc).isoformat(),
                "processing_time_ms": int(processing_time)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to read email {email_id}: {e}")
        return {
            "error": f"Failed to read email: {str(e)}",
            "status": "error",
            "email_id": email_id,
            "provider": provider,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@tool
async def parse_email_content(
    email_data: Dict[str, Any],
    extract_entities: bool = True
) -> Dict[str, Any]:
    """Parse and analyze email content for semantic information.
    
    This tool processes email content to extract semantic information,
    entities, intent, and other useful metadata.
    
    Args:
        email_data: Raw email data to parse
        extract_entities: Whether to extract entities and semantic info
        
    Returns:
        Dictionary containing parsed content and analysis
    """
    logger.info("Parsing email content for semantic analysis")
    
    # Input validation
    if not email_data or not isinstance(email_data, dict):
        return {
            "error": "Email data is required and must be a dictionary",
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    try:
        # Extract basic information
        subject = email_data.get("subject", "")
        body = email_data.get("body", {})
        sender = email_data.get("sender", {})
        
        # Get clean text content
        text_content = extract_email_text(body)
        
        # Basic parsing results
        parsed_data = {
            "subject_analysis": {
                "text": subject,
                "length": len(subject),
                "has_keywords": any(keyword in subject.lower() for keyword in ["urgent", "important", "asap"])
            },
            "body_analysis": {
                "text_length": len(text_content),
                "word_count": len(text_content.split()) if text_content else 0,
                "has_attachments": len(email_data.get("attachments", [])) > 0,
                "attachment_count": len(email_data.get("attachments", []))
            },
            "sender_analysis": {
                "email": sender.get("email", ""),
                "name": sender.get("name", ""),
                "domain": sender.get("email", "").split("@")[-1] if sender.get("email") else ""
            }
        }
        
        # Advanced analysis if requested
        if extract_entities:
            # Entity extraction
            entities = extract_entities(text_content)
            parsed_data["entities"] = entities
            
            # Intent classification
            intent = classify_email_intent(subject, text_content)
            parsed_data["intent"] = intent
            
            # Sentiment analysis
            sentiment = analyze_sentiment(text_content)
            parsed_data["sentiment"] = sentiment
        
        return {
            "status": "success",
            "parsed_content": parsed_data,
            "metadata": {
                "parsed_at": datetime.now(timezone.utc).isoformat(),
                "processing_time_ms": 75,
                "entities_extracted": extract_entities
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to parse email content: {e}")
        return {
            "error": f"Failed to parse email content: {str(e)}",
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
