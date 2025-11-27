"""
HTTP utilities for making requests to the Braze API.
"""

import json
from logging import Logger
from typing import Any, Type, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from braze_mcp_write.utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


async def make_request(
    client: httpx.AsyncClient,
    base_url: str,
    url_path: str,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
    method: str = "GET",
) -> httpx.Response:
    """
    Make an HTTP request to the Braze API.
    
    Args:
        client: HTTP client instance
        base_url: Base URL for the Braze API
        url_path: Path to append to base URL
        params: Query parameters (for GET requests)
        body: Request body (for POST/PUT requests)
        method: HTTP method (GET, POST, PUT, DELETE)
    
    Returns:
        HTTP response object
    
    Raises:
        httpx.HTTPError: If the request fails
    """
    url = f"{base_url}/{url_path}"
    
    # Remove None values from params
    if params:
        params = {k: v for k, v in params.items() if v is not None}
    
    logger.debug(f"{method} {url}")
    if params:
        logger.debug(f"Params: {params}")
    if body:
        logger.debug(f"Body: {json.dumps(body, indent=2)}")
    
    try:
        if method.upper() == "GET":
            response = await client.get(url, params=params)
        elif method.upper() == "POST":
            response = await client.post(url, json=body)
        elif method.upper() == "PUT":
            response = await client.put(url, json=body)
        elif method.upper() == "DELETE":
            response = await client.delete(url, json=body)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP {e.response.status_code} error for {url}")
        logger.error(f"Response: {e.response.text}")
        raise
    except httpx.HTTPError as e:
        logger.error(f"HTTP error for {url}: {e}")
        raise


def handle_response(
    response: httpx.Response,
    model: Type[T] | Type[dict],
    operation: str,
    logger_instance: Logger,
) -> T | dict[str, Any]:
    """
    Handle and parse an HTTP response.
    
    Args:
        response: HTTP response object
        model: Pydantic model class or dict for parsing
        operation: Description of the operation (for logging)
        logger_instance: Logger instance for error reporting
    
    Returns:
        Parsed response as the specified model type or dict
    """
    try:
        data = response.json()
        
        # If model is dict, return raw data
        if model is dict:
            logger_instance.debug(f"Successfully completed {operation}")
            return data
        
        # Try to parse with Pydantic model
        try:
            parsed = model(**data)
            logger_instance.debug(f"Successfully completed {operation}")
            return parsed
        except ValidationError as e:
            logger_instance.warning(
                f"Failed to parse response for {operation} with model {model.__name__}: {e}"
            )
            logger_instance.warning("Returning raw response data instead")
            return data
    
    except json.JSONDecodeError as e:
        logger_instance.error(f"Failed to decode JSON response for {operation}: {e}")
        return {
            "error": "Failed to decode response",
            "operation": operation,
            "raw_response": response.text,
        }

