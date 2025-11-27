"""
User tracking and profile management write operations for Braze MCP server.

This module provides functions for updating user attributes, tracking events,
purchases, and managing user profiles.
"""

from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp_write.utils import get_braze_context, get_logger, handle_response, make_request

__register_mcp_tools__ = True

logger = get_logger(__name__)


# ============================================================================
# USER TRACK - ATTRIBUTES, EVENTS, PURCHASES
# ============================================================================


# @safe_write_operation(rate_limit_count=1000, rate_limit_window=60)
async def track_user_data(
    ctx: Context,
    attributes: list[dict[str, Any]] | None = None,
    events: list[dict[str, Any]] | None = None,
    purchases: list[dict[str, Any]] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Track user attributes, custom events, and purchases in a single request.

    This is the primary endpoint for updating user profiles and tracking behavior.
    You can batch multiple operations together for efficiency.

    Args:
        ctx: The MCP context
        attributes: List of attribute objects. Each contains external_id or user_alias, and custom attribute name/value pairs
        events: List of event objects. Each contains external_id or user_alias, name (required), time, and properties
        purchases: List of purchase objects. Each contains external_id or user_alias, product_id, currency, price, quantity, time, and properties
        dry_run: If True, validates but doesn't track

    Returns:
        Dictionary with processing results and any errors
    """
    url_path = "users/track"

    body: dict[str, Any] = {}

    if attributes:
        body["attributes"] = attributes
    if events:
        body["events"] = events
    if purchases:
        body["purchases"] = purchases

    if not any([attributes, events, purchases]):
        raise ValueError("Must provide at least one of: attributes, events, or purchases")

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, body=body, method="POST"
    )

    return handle_response(response, dict, "track user data", logger)


# ============================================================================
# CONVENIENCE WRAPPERS
# ============================================================================


async def update_user_attributes(
    ctx: Context,
    external_id: str | None = None,
    user_alias: dict[str, str] | None = None,
    attributes: dict[str, Any] = {},
    update_existing_only: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Update attributes for a single user.

    Convenience wrapper around track_user_data for updating a single user's attributes.

    Args:
        ctx: The MCP context
        external_id: User's external ID (provide this OR user_alias)
        user_alias: User alias object with alias_name and alias_label (provide this OR external_id)
        attributes: Dictionary of attribute name/value pairs to set
        update_existing_only: If True, only update existing users (don't create new)
        dry_run: If True, validates but doesn't update

    Returns:
        Dictionary with update confirmation
    """
    if not external_id and not user_alias:
        raise ValueError("Must provide either external_id or user_alias")

    attribute_obj: dict[str, Any] = attributes.copy()

    if external_id:
        attribute_obj["external_id"] = external_id
    if user_alias:
        attribute_obj["user_alias"] = user_alias

    attribute_obj["_update_existing_only"] = update_existing_only

    return await track_user_data(ctx, attributes=[attribute_obj], dry_run=dry_run)


async def track_event(
    ctx: Context,
    event_name: str,
    external_id: str | None = None,
    user_alias: dict[str, str] | None = None,
    time: str | None = None,
    properties: dict[str, Any] | None = None,
    update_existing_only: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Track a custom event for a single user.

    Args:
        ctx: The MCP context
        event_name: Name of the custom event
        external_id: User's external ID (provide this OR user_alias)
        user_alias: User alias object (provide this OR external_id)
        time: ISO 8601 timestamp (defaults to now if not provided)
        properties: Dictionary of custom event properties
        update_existing_only: If True, only track for existing users
        dry_run: If True, validates but doesn't track

    Returns:
        Dictionary with tracking confirmation
    """
    if not external_id and not user_alias:
        raise ValueError("Must provide either external_id or user_alias")

    event_obj: dict[str, Any] = {"name": event_name}

    if external_id:
        event_obj["external_id"] = external_id
    if user_alias:
        event_obj["user_alias"] = user_alias
    if time:
        event_obj["time"] = time
    if properties:
        event_obj["properties"] = properties

    event_obj["_update_existing_only"] = update_existing_only

    return await track_user_data(ctx, events=[event_obj], dry_run=dry_run)


async def track_purchase(
    ctx: Context,
    product_id: str,
    currency: str,
    price: float,
    external_id: str | None = None,
    user_alias: dict[str, str] | None = None,
    quantity: int = 1,
    time: str | None = None,
    properties: dict[str, Any] | None = None,
    update_existing_only: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Track a purchase for a single user.

    Args:
        ctx: The MCP context
        product_id: Product identifier
        currency: ISO 4217 currency code (e.g., USD, EUR, GBP)
        price: Price as a number
        external_id: User's external ID (provide this OR user_alias)
        user_alias: User alias object (provide this OR external_id)
        quantity: Number of items purchased (default 1)
        time: ISO 8601 timestamp (defaults to now if not provided)
        properties: Dictionary of custom purchase properties
        update_existing_only: If True, only track for existing users
        dry_run: If True, validates but doesn't track

    Returns:
        Dictionary with tracking confirmation
    """
    if not external_id and not user_alias:
        raise ValueError("Must provide either external_id or user_alias")

    purchase_obj: dict[str, Any] = {
        "product_id": product_id,
        "currency": currency,
        "price": price,
        "quantity": quantity,
    }

    if external_id:
        purchase_obj["external_id"] = external_id
    if user_alias:
        purchase_obj["user_alias"] = user_alias
    if time:
        purchase_obj["time"] = time
    if properties:
        purchase_obj["properties"] = properties

    purchase_obj["_update_existing_only"] = update_existing_only

    return await track_user_data(ctx, purchases=[purchase_obj], dry_run=dry_run)


# ============================================================================
# USER DELETION
# ============================================================================


# @safe_write_operation(require_confirm=True)
async def delete_user(
    ctx: Context,
    external_id: str | None = None,
    user_alias: dict[str, str] | None = None,
    braze_id: str | None = None,
    dry_run: bool = False,
    confirm: bool = False,
) -> dict[str, Any]:
    """Delete a user from the Braze database.

    WARNING: This is a destructive operation that cannot be undone.
    The user will be permanently removed from Braze.

    Args:
        ctx: The MCP context
        external_id: User's external ID
        user_alias: User alias object with alias_name and alias_label
        braze_id: Braze's internal user ID
        dry_run: If True, validates but doesn't delete
        confirm: Must be True to execute this destructive operation

    Returns:
        Dictionary confirming the deletion
    """
    if not any([external_id, user_alias, braze_id]):
        raise ValueError("Must provide one of: external_id, user_alias, or braze_id")

    url_path = "users/delete"

    body: dict[str, Any] = {}

    if external_id:
        body["external_ids"] = [external_id]
    if user_alias:
        body["user_aliases"] = [user_alias]
    if braze_id:
        body["braze_ids"] = [braze_id]

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, body=body, method="POST"
    )

    return handle_response(response, dict, "delete user", logger)


# ============================================================================
# USER IDENTIFICATION (ALIAS TO EXTERNAL ID)
# ============================================================================


async def identify_users(
    ctx: Context,
    aliases_to_identify: list[dict[str, Any]],
    dry_run: bool = False,
) -> dict[str, Any]:
    """Identify users by associating an external_id with a user alias.

    This allows you to merge user profiles when you later learn a user's external_id
    but initially only had an alias.

    Args:
        ctx: The MCP context
        aliases_to_identify: List of identification objects. Each contains external_id and user_alias with alias_name and alias_label
        dry_run: If True, validates but doesn't identify

    Returns:
        Dictionary with identification results
    """
    url_path = "users/identify"

    body = {"aliases_to_identify": aliases_to_identify}

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, body=body, method="POST"
    )

    return handle_response(response, dict, "identify users", logger)

