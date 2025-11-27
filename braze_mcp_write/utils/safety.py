"""
Safety utilities for write operations in Braze MCP server.

This module provides decorators and utilities to ensure write operations
are only performed in safe, demo/POC environments.
"""

import os
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable

from mcp.server.fastmcp import Context

from braze_mcp_write.utils.context import get_braze_context
from braze_mcp_write.utils.logging import get_logger

logger = get_logger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

WRITE_ENABLED = os.getenv("BRAZE_WRITE_ENABLED", "false").lower() == "true"
ALLOW_PRODUCTION = os.getenv("BRAZE_ALLOW_PRODUCTION", "false").lower() == "true"
DRY_RUN_DEFAULT = os.getenv("BRAZE_DRY_RUN_DEFAULT", "false").lower() == "true"

# Workspace URL patterns that are allowed for write operations
ALLOWED_WORKSPACE_PATTERNS = os.getenv(
    "BRAZE_ALLOWED_WORKSPACES", "demo-,poc-,test-"
).split(",")

# Rate limits
MAX_SENDS_PER_HOUR = int(os.getenv("BRAZE_MAX_SENDS_PER_HOUR", "1000"))
MAX_CATALOG_UPDATES_PER_MIN = int(os.getenv("BRAZE_MAX_CATALOG_UPDATES_PER_MIN", "100"))

# ============================================================================
# RATE LIMITER
# ============================================================================


class RateLimiter:
    """Simple in-memory rate limiter for write operations."""

    def __init__(self):
        self.requests: dict[str, list[datetime]] = defaultdict(list)

    def check_limit(self, operation: str, limit: int, window_seconds: int) -> tuple[bool, str]:
        """
        Check if operation is within rate limit.
        
        Args:
            operation: Name of the operation being rate limited
            limit: Maximum number of requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            Tuple of (is_allowed, message)
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)

        # Clean old requests
        self.requests[operation] = [t for t in self.requests[operation] if t > cutoff]

        current_count = len(self.requests[operation])

        if current_count >= limit:
            wait_time = (self.requests[operation][0] - cutoff).total_seconds()
            return (
                False,
                f"Rate limit exceeded for {operation}. "
                f"{current_count}/{limit} requests in window. "
                f"Try again in {wait_time:.0f} seconds.",
            )

        self.requests[operation].append(now)
        return True, f"OK ({current_count + 1}/{limit})"


# Global rate limiter instance
rate_limiter = RateLimiter()

# ============================================================================
# VALIDATION DECORATORS
# ============================================================================


def validate_write_enabled(func: Callable) -> Callable:
    """
    Decorator to ensure write operations are enabled globally.
    
    Raises:
        ValueError: If BRAZE_WRITE_ENABLED is not set to true
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not WRITE_ENABLED:
            raise ValueError(
                f"Write operation '{func.__name__}' is disabled. "
                "Set BRAZE_WRITE_ENABLED=true to enable write operations."
            )
        return await func(*args, **kwargs)

    return wrapper


def validate_workspace_safety(func: Callable) -> Callable:
    """
    Decorator to validate that the workspace is safe for write operations.
    
    Only allows writes to workspaces matching ALLOWED_WORKSPACE_PATTERNS
    unless ALLOW_PRODUCTION is explicitly enabled.
    
    Raises:
        ValueError: If workspace is not in allowed list
    """

    @wraps(func)
    async def wrapper(ctx: Context, *args, **kwargs):
        bctx = get_braze_context(ctx)
        workspace_url = bctx.base_url

        if not ALLOW_PRODUCTION:
            # Check if workspace matches any allowed pattern
            is_allowed = any(
                pattern.strip() in workspace_url for pattern in ALLOWED_WORKSPACE_PATTERNS
            )

            if not is_allowed:
                raise ValueError(
                    f"Write operation '{func.__name__}' blocked for workspace: {workspace_url}\n"
                    f"Only workspaces matching these patterns are allowed: {ALLOWED_WORKSPACE_PATTERNS}\n"
                    "This is a safety measure to prevent accidental writes to production.\n"
                    "Set BRAZE_ALLOW_PRODUCTION=true to override (NOT RECOMMENDED)."
                )

            logger.info(
                f"Workspace safety check passed for {func.__name__}: {workspace_url}"
            )

        return await func(ctx, *args, **kwargs)

    return wrapper


def require_confirmation(operation_type: str = "destructive"):
    """
    Decorator factory for operations that require explicit confirmation.
    
    Args:
        operation_type: Type of operation (e.g., "destructive", "send", "delete")
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(ctx: Context, *args, **kwargs):
            # Extract operation details
            func_name = func.__name__

            # Get confirm parameter if it exists
            confirm = kwargs.pop("confirm", False)

            if not confirm:
                logger.warning(
                    f"⚠️  {operation_type.upper()} OPERATION BLOCKED: {func_name}\n"
                    f"   Args: {args}\n"
                    f"   Kwargs: {kwargs}\n"
                    f"   Add confirm=True to proceed with this operation."
                )
                return {
                    "error": f"{operation_type.capitalize()} operation requires confirmation",
                    "operation": func_name,
                    "message": "Add confirm=True parameter to proceed",
                    "parameters": {"args": args, "kwargs": kwargs},
                }

            logger.warning(f"✓ Confirmed {operation_type} operation: {func_name}")

            return await func(ctx, *args, **kwargs)

        return wrapper

    return decorator


def rate_limit(limit: int, window_seconds: int):
    """
    Decorator factory for rate limiting write operations.
    
    Args:
        limit: Maximum number of requests allowed
        window_seconds: Time window in seconds
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            operation_name = func.__name__

            is_allowed, message = rate_limiter.check_limit(
                operation_name, limit, window_seconds
            )

            if not is_allowed:
                logger.error(f"Rate limit exceeded for {operation_name}: {message}")
                raise ValueError(message)

            logger.debug(f"Rate limit check passed for {operation_name}: {message}")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# ============================================================================
# DRY RUN SUPPORT
# ============================================================================


def supports_dry_run(func: Callable) -> Callable:
    """
    Decorator to add dry run support to write operations.
    
    If dry_run=True (or default is enabled), logs the operation
    but doesn't actually perform it.
    """

    @wraps(func)
    async def wrapper(ctx: Context, *args, dry_run: bool | None = None, **kwargs):
        # Use provided dry_run value, or fall back to default
        should_dry_run = dry_run if dry_run is not None else DRY_RUN_DEFAULT

        if should_dry_run:
            logger.info(
                f"DRY RUN: {func.__name__}\n"
                f"  Args: {args}\n"
                f"  Kwargs: {kwargs}"
            )
            return {
                "dry_run": True,
                "operation": func.__name__,
                "would_execute": {
                    "function": func.__name__,
                    "args": args,
                    "kwargs": kwargs,
                },
                "message": "This is a dry run. No actual API call was made.",
            }

        return await func(ctx, *args, **kwargs)

    return wrapper


# ============================================================================
# COMBINED SAFETY DECORATOR
# ============================================================================


def safe_write_operation(
    rate_limit_count: int | None = None,
    rate_limit_window: int | None = None,
    require_confirm: bool = False,
):
    """
    Combined decorator that applies all safety checks for write operations.
    
    Args:
        rate_limit_count: Max requests allowed (None = no limit)
        rate_limit_window: Time window in seconds (None = no limit)
        require_confirm: Whether to require explicit confirmation
    
    Example:
        @safe_write_operation(rate_limit_count=100, rate_limit_window=3600, require_confirm=True)
        async def send_campaign(ctx: Context, campaign_id: str, ...):
            ...
    """

    def decorator(func: Callable) -> Callable:
        # Apply decorators in order (bottom to top execution)
        wrapped = func

        # 1. Dry run support (innermost - runs last)
        wrapped = supports_dry_run(wrapped)

        # 2. Rate limiting
        if rate_limit_count and rate_limit_window:
            wrapped = rate_limit(rate_limit_count, rate_limit_window)(wrapped)

        # 3. Confirmation requirement
        if require_confirm:
            wrapped = require_confirmation("destructive")(wrapped)

        # 4. Workspace validation
        wrapped = validate_workspace_safety(wrapped)

        # 5. Write enabled check (outermost - runs first)
        wrapped = validate_write_enabled(wrapped)

        return wrapped

    return decorator


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_workspace_info(ctx: Context) -> dict[str, Any]:
    """
    Get information about the current workspace.
    
    Args:
        ctx: MCP context
    
    Returns:
        Dictionary with workspace information
    """
    bctx = get_braze_context(ctx)

    return {
        "base_url": bctx.base_url,
        "write_enabled": WRITE_ENABLED,
        "allow_production": ALLOW_PRODUCTION,
        "allowed_patterns": ALLOWED_WORKSPACE_PATTERNS,
        "is_safe": any(
            pattern.strip() in bctx.base_url for pattern in ALLOWED_WORKSPACE_PATTERNS
        ),
    }


def log_write_operation(
    operation: str, parameters: dict[str, Any], result: Any = None, error: Any = None
) -> None:
    """
    Log a write operation for audit purposes.
    
    Args:
        operation: Name of the operation
        parameters: Parameters used
        result: Result of the operation (if successful)
        error: Error that occurred (if failed)
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "parameters": parameters,
    }

    if result:
        log_entry["result"] = "success"
        log_entry["data"] = result
        logger.info(f"Write operation completed: {log_entry}")
    elif error:
        log_entry["result"] = "error"
        log_entry["error"] = str(error)
        logger.error(f"Write operation failed: {log_entry}")
    else:
        logger.info(f"Write operation logged: {log_entry}")

