"""Email parsing utilities for MailMind."""

from __future__ import annotations

import html
import re
from typing import Dict, Any
from bs4 import BeautifulSoup


def parse_gmail_message(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Gmail message data into standardized format.
    
    Args:
        message_data: Raw Gmail API message data
        
    Returns:
        Standardized email dictionary
    """
    return message_data  # Already parsed by GmailClient


def extract_email_text(body_data: Dict[str, str]) -> str:
    """Extract clean text from email body.
    
    Args:
        body_data: Dictionary with 'text' and 'html' keys
        
    Returns:
        Clean text content
    """
    # Prefer plain text if available
    if body_data.get('text'):
        return body_data['text'].strip()
    
    # Fall back to HTML conversion
    if body_data.get('html'):
        return html_to_text(body_data['html'])
    
    return ""


def html_to_text(html_content: str) -> str:
    """Convert HTML content to plain text.
    
    Args:
        html_content: HTML string
        
    Returns:
        Plain text string
    """
    try:
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean up whitespace
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
        
    except Exception:
        # Fallback: basic HTML tag removal
        text = re.sub(r'<[^>]+>', '', html_content)
        text = html.unescape(text)
        return ' '.join(text.split())


def extract_entities(text: str) -> Dict[str, Any]:
    """Extract basic entities from email text.
    
    Args:
        text: Email text content
        
    Returns:
        Dictionary with extracted entities
    """
    entities = {
        "emails": [],
        "phone_numbers": [],
        "urls": [],
        "dates": [],
        "money": []
    }
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    entities["emails"] = re.findall(email_pattern, text)
    
    # Phone number pattern (basic)
    phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'
    entities["phone_numbers"] = re.findall(phone_pattern, text)
    
    # URL pattern
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    entities["urls"] = re.findall(url_pattern, text)
    
    # Money pattern
    money_pattern = r'\$[0-9,]+\.?[0-9]*'
    entities["money"] = re.findall(money_pattern, text)
    
    return entities


def classify_email_intent(subject: str, body: str) -> Dict[str, Any]:
    """Classify email intent based on content.
    
    Args:
        subject: Email subject
        body: Email body text
        
    Returns:
        Intent classification dictionary
    """
    text = f"{subject} {body}".lower()
    
    # Define intent patterns
    intent_patterns = {
        "meeting": ["meeting", "schedule", "appointment", "calendar", "call"],
        "task": ["task", "todo", "action item", "deadline", "complete"],
        "question": ["?", "question", "help", "how", "what", "when", "where", "why"],
        "information": ["info", "update", "report", "status", "summary"],
        "request": ["please", "can you", "could you", "would you", "need"],
        "urgent": ["urgent", "asap", "immediately", "important", "priority"],
        "social": ["thank", "congratulations", "birthday", "holiday"]
    }
    
    scores = {}
    for intent, keywords in intent_patterns.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > 0:
            scores[intent] = score
    
    if not scores:
        return {
            "category": "general",
            "confidence": 0.5,
            "keywords": []
        }
    
    # Get highest scoring intent
    top_intent = max(scores.keys(), key=lambda k: scores[k])
    max_score = scores[top_intent]
    total_keywords = sum(len(keywords) for keywords in intent_patterns.values())
    confidence = min(max_score / 5.0, 1.0)  # Normalize confidence
    
    return {
        "category": top_intent,
        "confidence": confidence,
        "keywords": intent_patterns[top_intent]
    }


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Basic sentiment analysis of email content.
    
    Args:
        text: Email text content
        
    Returns:
        Sentiment analysis dictionary
    """
    text_lower = text.lower()
    
    # Simple positive/negative word lists
    positive_words = [
        "good", "great", "excellent", "amazing", "wonderful", "fantastic",
        "thank", "thanks", "appreciate", "love", "best", "perfect",
        "happy", "pleased", "excited", "congratulations"
    ]
    
    negative_words = [
        "bad", "terrible", "awful", "horrible", "hate", "angry",
        "disappointed", "frustrated", "problem", "issue", "error",
        "wrong", "failed", "sorry", "apologize", "urgent", "critical"
    ]
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        sentiment = "positive"
        score = min((positive_count - negative_count) / 10.0, 1.0)
    elif negative_count > positive_count:
        sentiment = "negative"
        score = -min((negative_count - positive_count) / 10.0, 1.0)
    else:
        sentiment = "neutral"
        score = 0.0
    
    return {
        "sentiment": sentiment,
        "score": score,
        "confidence": min(abs(score) + 0.3, 1.0),
        "positive_words": positive_count,
        "negative_words": negative_count
    }
