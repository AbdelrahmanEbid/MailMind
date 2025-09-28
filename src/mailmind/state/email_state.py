"""Email state management for MailMind system."""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import Annotated, Any, Dict, List, Optional, Sequence

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


@dataclass(kw_only=True)
class InputState:
    """Input state for MailMind - defines the external interface.
    
    This represents what users provide when interacting with the system.
    It serves as a clean interface between external requests and internal processing.
    """

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(default_factory=list)
    """Messages in the conversation. Uses add_messages reducer for intelligent merging."""

    user_id: str = field(default="default_user")
    """Unique identifier for the user making the request."""

    email_provider: str = field(default="gmail")
    """Email provider to use (gmail for now)."""


@dataclass(kw_only=True)
class OutputState:
    """Output state for MailMind - defines what users receive.
    
    This represents the final response structure returned to users.
    """

    result: Dict[str, Any] = field(default_factory=dict)
    """Main result data (email content, search results, draft, etc.)."""

    status: str = field(default="pending")
    """Operation status (success, error, pending)."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata about the operation."""

    message: str = field(default="")
    """Human-readable message describing the result."""


