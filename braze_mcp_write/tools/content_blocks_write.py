"""
Content block write operations for Braze MCP server.

This module provides functions for creating and updating content blocks.
"""

from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp_write.utils import get_braze_context, get_logger, handle_response, make_request

__register_mcp_tools__ = True

logger = get_logger(__name__)


# ============================================================================
# CONTENT BLOCK OPERATIONS
# ============================================================================


async def create_content_block(
    ctx: Context,
    name: str,
    content: str,
    description: str = "",
    content_type: str = "html",
    tags: list[str] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Create a new content block.

    Content blocks are reusable content that can be referenced in messages.

    Args:
        ctx: The MCP context
        name: Name of the content block
        content: The actual content (HTML, text, or liquid)
        description: Optional description of the content block
        content_type: Type of content (html, text, or liquid). Defaults to html
        tags: Optional list of tags for organization
        dry_run: If True, validates but doesn't create

    Returns:
        Dictionary with content block creation confirmation including content_block_id
    """
    url_path = "content_blocks/create"

    body: dict[str, Any] = {
        "name": name,
        "content": content,
        "content_type": content_type,
    }

    if description:
        body["description"] = description
    if tags:
        body["tags"] = tags

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, body=body, method="POST"
    )

    return handle_response(response, dict, "create content block", logger)


async def update_content_block(
    ctx: Context,
    content_block_id: str,
    name: str | None = None,
    content: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Update an existing content block.

    Args:
        ctx: The MCP context
        content_block_id: ID of the content block to update
        name: New name (optional)
        content: New content (optional)
        description: New description (optional)
        tags: New tags list (optional)
        dry_run: If True, validates but doesn't update

    Returns:
        Dictionary with update confirmation
    """
    url_path = "content_blocks/update"

    body: dict[str, Any] = {
        "content_block_id": content_block_id,
    }

    if name is not None:
        body["name"] = name
    if content is not None:
        body["content"] = content
    if description is not None:
        body["description"] = description
    if tags is not None:
        body["tags"] = tags

    if len(body) == 1:  # Only content_block_id provided
        raise ValueError("Must provide at least one field to update")

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, body=body, method="POST"
    )

    return handle_response(response, dict, "update content block", logger)

