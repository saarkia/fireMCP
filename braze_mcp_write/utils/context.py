"""
Context management for Braze MCP Write Server.

Handles Braze API context including authentication, base URL, and HTTP client lifecycle.
"""

import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncGenerator

import httpx
from mcp.server.fastmcp import Context

from braze_mcp_write.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class BrazeContext:
    """
    Braze API context containing configuration and HTTP client.
    """
    api_key: str
    base_url: str
    http_client: httpx.AsyncClient


def get_braze_context(ctx: Context) -> BrazeContext:
    """
    Extract Braze context from MCP context.
    
    Args:
        ctx: MCP context
    
    Returns:
        BrazeContext with API configuration and HTTP client
    
    Raises:
        ValueError: If Braze context is not properly initialized
    """
    if not hasattr(ctx, "request_context") or not isinstance(ctx.request_context, BrazeContext):
        raise ValueError(
            "Braze context not found. Ensure the server is properly initialized "
            "with braze_lifespan."
        )
    return ctx.request_context


@asynccontextmanager
async def braze_lifespan(server: Any) -> AsyncGenerator[BrazeContext, None]:
    """
    Lifespan context manager for the Braze MCP server.
    
    Initializes HTTP client and validates configuration on startup,
    cleans up resources on shutdown.
    
    Args:
        server: The FastMCP server instance
    
    Yields:
        BrazeContext for use in request handlers
    
    Raises:
        ValueError: If required environment variables are missing
    """
    # Validate required environment variables
    api_key = os.getenv("BRAZE_API_KEY")
    base_url = os.getenv("BRAZE_BASE_URL")
    
    if not api_key:
        raise ValueError(
            "BRAZE_API_KEY environment variable is required. "
            "Please set it to your Braze REST API key."
        )
    
    if not base_url:
        raise ValueError(
            "BRAZE_BASE_URL environment variable is required. "
            "Please set it to your Braze REST API endpoint "
            "(e.g., https://rest.iad-01.braze.com)"
        )
    
    # Remove trailing slash from base URL
    base_url = base_url.rstrip("/")
    
    logger.info(f"Initializing Braze MCP Write Server")
    logger.info(f"Base URL: {base_url}")
    logger.info(f"Write operations enabled: {os.getenv('BRAZE_WRITE_ENABLED', 'false')}")
    
    # Create HTTP client
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    
    braze_ctx = BrazeContext(
        api_key=api_key,
        base_url=base_url,
        http_client=http_client,
    )
    
    try:
        yield braze_ctx
    finally:
        logger.info("Shutting down Braze MCP Write Server")
        await http_client.aclose()

