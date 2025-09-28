"""Tools for MailMind email operations."""

from mailmind.tools.email_reader import read_email_by_id, parse_email_content
READER_TOOLS = [read_email_by_id, parse_email_content]
__all__ = [
    "read_email_by_id",
    "parse_email_content", 
    "READER_TOOLS",
]
