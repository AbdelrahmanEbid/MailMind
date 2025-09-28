"""Utility functions for MailMind."""

from mailmind.utils.gmail_client import GmailClient
from mailmind.utils.email_parser import (
    parse_gmail_message, 
    extract_email_text,
    extract_entities,
    classify_email_intent,
    analyze_sentiment
)

__all__ = [
    "GmailClient",
    "parse_gmail_message",
    "extract_email_text",
    "extract_entities",
    "classify_email_intent",
    "analyze_sentiment",
]

