"""
Canvas write operations for Braze MCP server.

This module provides functions for triggering and managing Canvas flows.
"""

from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp_write.utils import get_braze_context, get_logger, handle_response, make_request

__register_mcp_tools__ = True

logger = get_logger(__name__)


# ============================================================================
# CANVAS TRIGGERING
# ============================================================================


async def trigger_canvas(
    ctx: Context,
    canvas_id: str,
    recipients: list[dict[str, Any]] | None = None,
    canvas_entry_properties: dict[str, Any] | None = None,
    broadcast: bool = False,
    audience: dict[str, Any] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Trigger a Canvas for specified recipients.

    This endpoint allows you to trigger Canvas flows via the API.

    Args:
        ctx: The MCP context
        canvas_id: The Canvas identifier to trigger
        recipients: List of recipient objects. Each contains external_user_id or user_alias, and optional canvas_entry_properties
        canvas_entry_properties: Properties to pass to all recipients (merged with individual recipient properties)
        broadcast: If True, send to entire segment defined in Canvas
        audience: Audience definition with connected_audience or segment filters
        dry_run: If True, validates but doesn't trigger

    Returns:
        Dictionary with trigger confirmation and dispatch_id
    """
    url_path = "canvas/trigger/send"

    body: dict[str, Any] = {
        "canvas_id": canvas_id,
        "broadcast": broadcast,
    }

    if recipients:
        body["recipients"] = recipients
    if canvas_entry_properties:
        body["canvas_entry_properties"] = canvas_entry_properties
    if audience:
        body["audience"] = audience

    # Validation
    if not broadcast and not recipients:
        raise ValueError("recipients is required when broadcast=False")

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, body=body, method="POST"
    )

    return handle_response(response, dict, "trigger canvas", logger)


async def schedule_canvas(
    ctx: Context,
    canvas_id: str,
    send_at: str,
    recipients: list[dict[str, Any]] | None = None,
    canvas_entry_properties: dict[str, Any] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Schedule a Canvas to be triggered at a specific time.

    Args:
        ctx: The MCP context
        canvas_id: The Canvas identifier to schedule
        send_at: ISO 8601 timestamp for when to trigger the Canvas
        recipients: List of recipient objects (external_user_id or user_alias)
        canvas_entry_properties: Properties to pass to all recipients
        dry_run: If True, validates but doesn't schedule

    Returns:
        Dictionary with schedule confirmation
    """
    url_path = "canvas/trigger/schedule/create"

    body: dict[str, Any] = {
        "canvas_id": canvas_id,
        "send_at": send_at,
    }

    if recipients:
        body["recipients"] = recipients
    if canvas_entry_properties:
        body["canvas_entry_properties"] = canvas_entry_properties

    if not recipients:
        raise ValueError("recipients is required for scheduled Canvas")

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, body=body, method="POST"
    )

    return handle_response(response, dict, "schedule canvas", logger)


async def update_canvas_schedule(
    ctx: Context,
    canvas_id: str,
    schedule_id: str,
    send_at: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Update the trigger time for a scheduled Canvas.

    Args:
        ctx: The MCP context
        canvas_id: The Canvas identifier
        schedule_id: The schedule identifier to update
        send_at: New ISO 8601 timestamp for when to trigger
        dry_run: If True, validates but doesn't update

    Returns:
        Dictionary with update confirmation
    """
    url_path = "canvas/trigger/schedule/update"

    body = {
        "canvas_id": canvas_id,
        "schedule_id": schedule_id,
        "send_at": send_at,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, body=body, method="POST"
    )

    return handle_response(response, dict, "update canvas schedule", logger)


async def delete_scheduled_canvas(
    ctx: Context,
    canvas_id: str,
    schedule_id: str,
    dry_run: bool = False,
    confirm: bool = False,
) -> dict[str, Any]:
    """Delete a scheduled Canvas trigger.

    Args:
        ctx: The MCP context
        canvas_id: The Canvas identifier
        schedule_id: The schedule identifier to delete
        dry_run: If True, validates but doesn't delete
        confirm: Must be True to execute this operation

    Returns:
        Dictionary with deletion confirmation
    """
    if not confirm and not dry_run:
        return {
            "error": "Confirmation required",
            "message": "Set confirm=True to delete scheduled canvas",
        }

    url_path = "canvas/trigger/schedule/delete"

    body = {
        "canvas_id": canvas_id,
        "schedule_id": schedule_id,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, body=body, method="POST"
    )

    return handle_response(response, dict, "delete scheduled canvas", logger)

