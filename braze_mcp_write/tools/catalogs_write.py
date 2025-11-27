"""
Catalog management write operations for Braze MCP server.

This module provides functions for creating, updating, and deleting catalog items.
"""

from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp_write.utils import get_braze_context, get_logger, handle_response, make_request

__register_mcp_tools__ = True

logger = get_logger(__name__)


# ============================================================================
# CATALOG ITEM OPERATIONS
# ============================================================================


async def create_catalog_items(
    ctx: Context,
    catalog_name: str,
    items: list[dict[str, Any]],
    dry_run: bool = False,
) -> dict[str, Any]:
    """Create new items in a catalog.

    Args:
        ctx: The MCP context
        catalog_name: Name of the catalog
        items: List of item objects to create. Each must have an id field and can have any custom fields
        dry_run: If True, validates but doesn't create

    Returns:
        Dictionary with creation confirmation
    """
    url_path = f"catalogs/{catalog_name}/items"

    body = {"items": items}

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, body=body, method="POST"
    )

    return handle_response(response, dict, "create catalog items", logger)


async def update_catalog_items(
    ctx: Context,
    catalog_name: str,
    items: list[dict[str, Any]],
    dry_run: bool = False,
) -> dict[str, Any]:
    """Update existing items in a catalog.

    Args:
        ctx: The MCP context
        catalog_name: Name of the catalog
        items: List of item objects to update. Each must have an id field matching an existing item
        dry_run: If True, validates but doesn't update

    Returns:
        Dictionary with update confirmation
    """
    url_path = f"catalogs/{catalog_name}/items"

    body = {"items": items}

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, body=body, method="PUT"
    )

    return handle_response(response, dict, "update catalog items", logger)


async def delete_catalog_items(
    ctx: Context,
    catalog_name: str,
    item_ids: list[str],
    dry_run: bool = False,
    confirm: bool = False,
) -> dict[str, Any]:
    """Delete items from a catalog.

    Args:
        ctx: The MCP context
        catalog_name: Name of the catalog
        item_ids: List of item IDs to delete
        dry_run: If True, validates but doesn't delete
        confirm: Must be True to execute this destructive operation

    Returns:
        Dictionary with deletion confirmation
    """
    if not confirm and not dry_run:
        return {
            "error": "Confirmation required",
            "message": "Set confirm=True to delete catalog items",
        }

    url_path = f"catalogs/{catalog_name}/items"

    body = {"items": [{"id": item_id} for item_id in item_ids]}

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, body=body, method="DELETE"
    )

    return handle_response(response, dict, "delete catalog items", logger)


# ============================================================================
# CATALOG MANAGEMENT
# ============================================================================


async def create_catalog(
    ctx: Context,
    name: str,
    description: str,
    fields: list[dict[str, str]],
    dry_run: bool = False,
) -> dict[str, Any]:
    """Create a new catalog.

    Args:
        ctx: The MCP context
        name: Name of the catalog (must be unique)
        description: Description of the catalog
        fields: List of field definitions. Each contains name and type (string, number, boolean, time)
        dry_run: If True, validates but doesn't create

    Returns:
        Dictionary with catalog creation confirmation
    """
    url_path = "catalogs"

    body = {
        "catalogs": [
            {
                "name": name,
                "description": description,
                "fields": fields,
            }
        ]
    }

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, body=body, method="POST"
    )

    return handle_response(response, dict, "create catalog", logger)


async def delete_catalog(
    ctx: Context,
    catalog_name: str,
    dry_run: bool = False,
    confirm: bool = False,
) -> dict[str, Any]:
    """Delete a catalog and all its items.

    WARNING: This is a destructive operation that cannot be undone.
    All items in the catalog will be permanently deleted.

    Args:
        ctx: The MCP context
        catalog_name: Name of the catalog to delete
        dry_run: If True, validates but doesn't delete
        confirm: Must be True to execute this destructive operation

    Returns:
        Dictionary with deletion confirmation
    """
    if not confirm and not dry_run:
        return {
            "error": "Confirmation required",
            "message": "Set confirm=True to delete catalog. This will delete all items in the catalog.",
        }

    url_path = f"catalogs/{catalog_name}"

    bctx = get_braze_context(ctx)

    response = await make_request(
        bctx.http_client, bctx.base_url, url_path, method="DELETE"
    )

    return handle_response(response, dict, "delete catalog", logger)

