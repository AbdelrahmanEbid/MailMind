"""Main graph implementation for MailMind."""

from __future__ import annotations

import logging
from typing import Optional
from langgraph.graph import END, START, StateGraph
from mailmind.agents import (
    create_reader_agent,
)
from mailmind.config import MailMindConfig
from mailmind.state import InputState, OutputState

logger = logging.getLogger(__name__)
def create_simple_reader_graph(config: Optional[MailMindConfig] = None):
    """Create a simplified graph with just the reader agent for testing.
    
    This is useful for testing and development when you only need
    email reading functionality.
    
    Args:
        config: MailMind configuration (creates default if None)
        
    Returns:
        Compiled LangGraph with reader agent only
    """
    logger.info("Creating simple reader graph")
    
    if config is None:
        config = MailMindConfig()
    
    reader_agent = create_reader_agent(config)
    
    builder = StateGraph(
        input_schema=InputState,
        output_schema=OutputState,
        config_schema=MailMindConfig
    )
    
    builder.add_node("reader", reader_agent)
    builder.add_edge(START, "reader")
    builder.add_edge("reader", END)
    
    graph = builder.compile(name="SimpleReader")
    
    logger.info("Simple reader graph compiled successfully")
    return graph

