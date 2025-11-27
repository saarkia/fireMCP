"""
Error models and response utilities for Braze MCP Write Server.
"""

from typing import Any


def function_not_found_error(function_name: str, available_functions: list[str]) -> dict[str, Any]:
    """
    Create an error response for a function not found.
    
    Args:
        function_name: Name of the function that was not found
        available_functions: List of available function names
    
    Returns:
        Error dictionary
    """
    return {
        "error": "Function not found",
        "function": function_name,
        "message": f"Function '{function_name}' is not available",
        "available_functions": available_functions[:10],  # Show first 10
        "total_available": len(available_functions),
        "suggestion": "Use list_functions() to see all available functions",
    }


def invalid_params_error(message: str, operation: str) -> dict[str, Any]:
    """
    Create an error response for invalid parameters.
    
    Args:
        message: Error message describing the issue
        operation: Name of the operation that failed
    
    Returns:
        Error dictionary
    """
    return {
        "error": "Invalid parameters",
        "operation": operation,
        "message": message,
    }


def internal_error(message: str, operation: str) -> dict[str, Any]:
    """
    Create an error response for internal errors.
    
    Args:
        message: Error message
        operation: Name of the operation that failed
    
    Returns:
        Error dictionary
    """
    return {
        "error": "Internal error",
        "operation": operation,
        "message": message,
    }

