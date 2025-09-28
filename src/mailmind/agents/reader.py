"""Reader agent for MailMind - specializes in email reading and parsing."""

from __future__ import annotations

import logging
from typing import Dict, Any

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

from mailmind.config import MailMindConfig
from mailmind.tools import READER_TOOLS

logger = logging.getLogger(__name__)


def create_reader_agent(config: MailMindConfig):
    """Create the reader agent for email reading operations.
    
    The reader agent specializes in:
    1. Reading emails by ID or other criteria
    2. Parsing email content and structure
    3. Extracting semantic information from emails
    4. Analyzing email metadata and attachments
    
    Args:
        config: MailMind configuration
        
    Returns:
        Configured reader agent
    """
    logger.info("Creating reader agent")
    
    # Initialize the LLM
    if "/" in config.model:
        provider, model_name = config.model.split("/", 1)
        model = init_chat_model(
            model_name,
            model_provider=provider,
            temperature=config.model_temperature,
            max_tokens=config.max_tokens,
        )
    else:
        # For Google Gemini models, specify the provider explicitly
        model = init_chat_model(
            config.model,
            model_provider="google_genai",
            temperature=config.model_temperature,
            max_tokens=config.max_tokens,
        )
    
    # Reader agent system prompt
    system_prompt = f"""You are the MailMind Reader Agent, a specialist in email reading and analysis.

Your expertise includes:
1. Reading emails by ID from email providers
2. Parsing email structure (headers, body, attachments)
3. Extracting semantic information (intent, entities, sentiment)
4. Analyzing email metadata and relationships

Available tools:
- read_email_by_id: Read a specific email using its unique identifier
- parse_email_content: Analyze email content for semantic information

Guidelines:
- Always validate email IDs before attempting to read
- Provide comprehensive analysis of email content
- Extract meaningful insights from email structure and content
- Handle errors gracefully and provide helpful error messages
- Focus on accuracy and completeness in email analysis

Current configuration:
- Email Provider: {config.email_provider}
- Max Email Length: {config.max_email_length} characters
- Timeout: {config.timeout_seconds} seconds

When you complete your analysis, provide:
1. A summary of the email content
2. Key information extracted (sender, subject, main points)
3. Any semantic insights (intent, sentiment, entities)
4. Recommendations for follow-up actions if applicable

Be thorough, accurate, and helpful in your email analysis."""

    # Create the ReAct agent with reader tools
    reader = create_react_agent(
        model=model,
        tools=READER_TOOLS,
        prompt=system_prompt,
        name="reader_agent"
    )
    
    logger.info("Reader agent created successfully")
    return reader
