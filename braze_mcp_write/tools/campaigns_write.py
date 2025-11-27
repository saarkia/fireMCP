"""
Campaign write operations for Braze MCP server.

This module provides functions for sending, creating, and managing campaigns.
"""

from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp_write.utils import get_braze_context, get_logger, handle_response, make_request

__register_mcp_tools__ = True

logger = get_logger(__name__)


# ============================================================================
# CAMPAIGN SENDING
# ============================================================================


async def send_campaign(
    ctx: Context,
    campaign_id: str,
    send_id: str | None = None,
    override_frequency_capping: bool = False,
    recipients: list[dict[str, Any]] | None = None,
    segment_id: str | None = None,
    broadcast: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Send a campaign to specified recipients or segment.

    This endpoint allows you to send immediate campaign messages via API-triggered delivery.

    Args:
        ctx: The MCP context
        campaign_id: The campaign identifier to send
        send_id: Optional send identifier for tracking (generated if not provided)
        override_frequency_capping: If True, ignore frequency capping settings
        recipients: List of recipient objects. Each contains external_user_id or user_alias, and optional trigger_properties
        segment_id: ID of a segment to send to (alternative to recipients)
        broadcast: If True, send to entire segment (requires segment_id)
        dry_run: If True, validates but doesn't send

    Returns:
        Dictionary with send confirmation and dispatch_id
    """
    url_path = "campaigns/trigger/send"

    body: dict[str, Any] = {
        "campaign_id": campaign_id,
        "broadcast": broadcast,
    }

    if send_id:
        body["send_id"] = send_id
    if override_frequency_capping:
        body["override_frequency_capping"] = override_frequency_capping
    if recipients:
        body["recipients"] = recipients
    if segment_id:
        body["segment_id"] = segment_id

    # Validation
    if broadcast and not segment_id:
        raise ValueError("segment_id is required when broadcast=True")
    if not broadcast and not recipients:
        raise ValueError("recipients is required when broadcast=False")

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, body=body, method="POST"
    )

    return handle_response(response, dict, "send campaign", logger)


async def schedule_campaign(
    ctx: Context,
    campaign_id: str,
    send_at: str,
    recipients: list[dict[str, Any]] | None = None,
    segment_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Schedule a campaign to be sent at a specific time.

    Args:
        ctx: The MCP context
        campaign_id: The campaign identifier to schedule
        send_at: ISO 8601 timestamp for when to send the campaign
        recipients: List of recipient objects (external_user_id or user_alias)
        segment_id: ID of a segment to send to (alternative to recipients)
        dry_run: If True, validates but doesn't schedule

    Returns:
        Dictionary with schedule confirmation
    """
    url_path = "campaigns/trigger/schedule/create"

    body: dict[str, Any] = {
        "campaign_id": campaign_id,
        "send_at": send_at,
    }

    if recipients:
        body["recipients"] = recipients
    if segment_id:
        body["segment_id"] = segment_id

    if not recipients and not segment_id:
        raise ValueError("Must provide either recipients or segment_id")

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, body=body, method="POST"
    )

    return handle_response(response, dict, "schedule campaign", logger)


# ============================================================================
# CAMPAIGN MANAGEMENT
# ============================================================================


async def update_campaign_schedule(
    ctx: Context,
    campaign_id: str,
    schedule_id: str,
    send_at: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Update the send time for a scheduled campaign.

    Args:
        ctx: The MCP context
        campaign_id: The campaign identifier
        schedule_id: The schedule identifier to update
        send_at: New ISO 8601 timestamp for when to send
        dry_run: If True, validates but doesn't update

    Returns:
        Dictionary with update confirmation
    """
    url_path = "campaigns/trigger/schedule/update"

    body = {
        "campaign_id": campaign_id,
        "schedule_id": schedule_id,
        "send_at": send_at,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, body=body, method="POST"
    )

    return handle_response(response, dict, "update campaign schedule", logger)


async def delete_scheduled_campaign(
    ctx: Context,
    campaign_id: str,
    schedule_id: str,
    dry_run: bool = False,
    confirm: bool = False,
) -> dict[str, Any]:
    """Delete a scheduled campaign send.

    Args:
        ctx: The MCP context
        campaign_id: The campaign identifier
        schedule_id: The schedule identifier to delete
        dry_run: If True, validates but doesn't delete
        confirm: Must be True to execute this operation

    Returns:
        Dictionary with deletion confirmation
    """
    if not confirm and not dry_run:
        return {
            "error": "Confirmation required",
            "message": "Set confirm=True to delete scheduled campaign",
        }

    url_path = "campaigns/trigger/schedule/delete"

    body = {
        "campaign_id": campaign_id,
        "schedule_id": schedule_id,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, body=body, method="POST"
    )

    return handle_response(response, dict, "delete scheduled campaign", logger)

