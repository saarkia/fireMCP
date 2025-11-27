"""
Registry builder for auto-discovering and registering MCP tools.

This module uses reflection to scan braze_mcp_write.tools for modules with
__register_mcp_tools__ = True and automatically extracts their metadata.
"""

import importlib
import inspect
import json
import pkgutil
from typing import Any, Type, Union, get_args, get_origin, get_type_hints

import braze_mcp_write.tools
from braze_mcp_write.utils.logging import get_logger

logger = get_logger(__name__)

# ============================================================================
# DOCSTRING CONVENTIONS & VALIDATION
# ============================================================================

"""
DOCSTRING CONVENTIONS FOR MCP TOOLS

This module auto-generates function metadata from docstrings using Google-style conventions.

QUICK REFERENCE:
- Use 'Args:' and 'Returns:' sections
- Document all parameters except 'ctx'
- Indent parameter descriptions with spaces
- Follow format: "param_name: description"

VALIDATION: Functions validate automatically during registration. Invalid docstrings FAIL registration.
"""

DOCSTRING_SECTION_HEADERS = [
    "args:",
    "arguments:",
    "parameters:",
    "returns:",
    "return:",
    "raises:",
    "raise:",
    "yields:",
    "yield:",
    "examples:",
    "example:",
    "note:",
    "notes:",
    "warning:",
    "warnings:",
]

BASIC_TYPE_MAPPING = {
    str: "string",
    int: "integer",
    bool: "boolean",
    float: "number",
    list: "array",
    dict: "object",
    object: "object",
}


# ============================================================================
# TYPE CONVERSION
# ============================================================================


def _python_type_to_json_type(python_type) -> str:
    """Convert Python type hints to JSON schema types"""
    try:
        if python_type is type(None):
            return "null"

        origin = get_origin(python_type)
        args = get_args(python_type)

        # Handle Union types (including Optional[T])
        if origin is Union or str(type(python_type)).endswith("UnionType'>"):
            non_none_types = [t for t in args if t is not type(None)]
            if non_none_types:
                return _python_type_to_json_type(non_none_types[0])
            return "null"

        # Handle generic types
        if origin is not None:
            if origin in (list, tuple):
                return "array"
            elif origin is dict:
                return "object"
            else:
                python_type = origin

        return BASIC_TYPE_MAPPING.get(python_type, "object")

    except Exception:
        return "string"


def _safe_serialize_default(default_value) -> Any:
    """Safely serialize default values to JSON-compatible format"""
    try:
        json.dumps(default_value)
        return default_value
    except (TypeError, ValueError):
        if default_value is None:
            return None
        elif callable(default_value):
            return f"<function: {getattr(default_value, '__name__', 'unknown')}>"
        elif hasattr(default_value, "__class__"):
            return f"<{default_value.__class__.__name__}: {str(default_value)}>"
        else:
            return str(default_value)


# ============================================================================
# DOCSTRING PARSING
# ============================================================================


def _extract_description_from_docstring(docstring: str | None) -> str:
    """Extract main description from function docstring"""
    if not docstring:
        return "No description available"

    lines = docstring.split("\n")
    description_lines = []
    found_content = False

    for line in lines:
        stripped = line.strip()

        if not stripped and not found_content:
            continue

        # Stop at section headers
        if _is_section_header(line, DOCSTRING_SECTION_HEADERS, check_indentation=False):
            break

        if stripped:
            description_lines.append(stripped)
            found_content = True

    return " ".join(description_lines) if description_lines else "No description available"


def _is_section_header(
    line: str, valid_sections: list | None = None, check_indentation: bool = True
) -> bool:
    """Check if a line is a docstring section header"""
    stripped = line.strip()

    if not (stripped and stripped.endswith(":")):
        return False

    if check_indentation and line.startswith((" ", "\t")):
        return False

    if valid_sections is not None:
        return stripped.lower() in valid_sections

    return True


def _find_section_start(lines: list, section_names: list) -> int | None:
    """Find the start line index of a docstring section"""
    for i, line in enumerate(lines):
        if _is_section_header(line, section_names, check_indentation=False):
            return i + 1
    return None


def _parse_args_section(docstring: str, param_name: str) -> str | None:
    """Parse the Args section of a docstring to find parameter descriptions"""
    lines = docstring.split("\n")
    args_start = _find_section_start(lines, ["args:", "arguments:", "parameters:"])

    if args_start is None:
        return None

    for i in range(args_start, len(lines)):
        line = lines[i]
        stripped = line.strip()

        # Stop at next section
        if _is_section_header(line):
            break

        if ":" not in stripped:
            continue

        param_part, desc_part = stripped.split(":", 1)
        param_part = param_part.strip()

        # Match exact parameter name or with type annotation
        if param_part == param_name or param_part.startswith(f"{param_name} ("):
            desc_part = desc_part.strip()
            if desc_part:
                return _extract_multiline_description(lines, i, desc_part)

    return None


def _extract_multiline_description(lines: list, start_index: int, first_line: str) -> str:
    """Extract multiline description starting from a given line"""
    full_description = [first_line]
    base_indent = len(lines[start_index]) - len(lines[start_index].lstrip())

    for j in range(start_index + 1, len(lines)):
        next_line = lines[j]

        if not next_line.strip():
            continue

        next_indent = len(next_line) - len(next_line.lstrip())

        if next_indent > base_indent:
            full_description.append(next_line.strip())
        else:
            break

    return " ".join(full_description)


def _parse_returns_section(docstring: str | None) -> str | None:
    """Parse the Returns section of a docstring"""
    if not docstring:
        return None

    lines = docstring.split("\n")
    returns_start = _find_section_start(lines, ["returns:", "return:"])

    if returns_start is None:
        return None

    description_lines: list[str] = []

    for i in range(returns_start, len(lines)):
        line = lines[i]
        stripped = line.strip()

        # Stop at next section
        if _is_section_header(line):
            break

        if not stripped and not description_lines:
            continue

        if stripped:
            description_lines.append(stripped)
        elif description_lines:
            break

    return " ".join(description_lines) if description_lines else None


# ============================================================================
# PARAMETER EXTRACTION
# ============================================================================


def _extract_param_description(docstring: str | None, param_name: str, param_type) -> str:
    """Extract parameter description from docstring"""
    if not docstring:
        return f"Parameter {param_name}"

    args_description = _parse_args_section(docstring, param_name)
    return args_description if args_description else f"Parameter {param_name}"


def _extract_parameter_info(
    param_name: str,
    param: inspect.Parameter,
    type_hints: dict,
    docstring: str | None,
) -> dict:
    """Extract complete parameter information"""
    try:
        param_type = type_hints.get(param_name, str)

        param_info = {
            "type": _python_type_to_json_type(param_type),
            "required": param.default == inspect.Parameter.empty,
            "description": _extract_param_description(docstring, param_name, param_type),
        }

        if param.default != inspect.Parameter.empty:
            param_info["default"] = _safe_serialize_default(param.default)

        return param_info

    except Exception as e:
        logger.warning(f"Could not extract metadata for parameter {param_name}: {e}")
        return {
            "type": "string",
            "required": param.default == inspect.Parameter.empty,
            "description": f"Parameter {param_name}",
        }


# ============================================================================
# MAIN EXTRACTION FUNCTIONS
# ============================================================================


def extract_function_metadata(func) -> dict[str, Any]:
    """Extract metadata from a function for registry using introspection"""
    try:
        signature = inspect.signature(func)
        type_hints = _get_type_hints_safely(func)
        description = _extract_description_from_docstring(func.__doc__)

        parameters = {}
        for param_name, param in signature.parameters.items():
            parameters[param_name] = _extract_parameter_info(
                param_name, param, type_hints, func.__doc__
            )

        result = {
            "implementation": func,
            "description": description,
            "parameters": parameters,
        }

        # Add returns info if available
        returns_description = _parse_returns_section(func.__doc__)
        if returns_description:
            result["returns"] = {"description": returns_description, "type": "object"}

        return result

    except Exception as e:
        logger.exception(f"Failed to extract metadata for function {func.__name__}")
        return _create_fallback_metadata(func, str(e))


def _get_type_hints_safely(func) -> dict:
    """Safely get type hints from a function"""
    try:
        return get_type_hints(func)
    except (NameError, AttributeError, TypeError) as e:
        logger.warning(f"Could not get type hints for {func.__name__}: {e}")
        return {}


def _create_fallback_metadata(func, error: str) -> dict:
    """Create minimal fallback metadata when extraction fails"""
    return {
        "implementation": func,
        "description": f"Function {func.__name__} (metadata extraction failed)",
        "parameters": {},
        "error": error,
    }


# ============================================================================
# REGISTRY BUILDING
# ============================================================================


def _is_valid_function(obj, name: str) -> bool:
    """Check if an object is a valid function for the registry"""
    return (
        inspect.iscoroutinefunction(obj)
        and not name.startswith("_")
        and hasattr(obj, "__module__")
        and obj.__module__.startswith("braze_mcp_write.tools")
    )


def _discover_mcp_tool_modules():
    """Discover all modules in the tools package that have __register_mcp_tools__ = True"""
    discovered_modules = []

    for module_info in pkgutil.iter_modules(
        braze_mcp_write.tools.__path__, braze_mcp_write.tools.__name__ + "."
    ):
        try:
            module = importlib.import_module(module_info.name)

            if hasattr(module, "__register_mcp_tools__") and module.__register_mcp_tools__:
                discovered_modules.append(module)
                logger.info(f"Discovered MCP tools module: {module_info.name}")

        except Exception as e:
            logger.warning(f"Failed to import module {module_info.name}: {e}")

    return discovered_modules


def build_function_registry() -> dict[str, dict[str, Any]]:
    """Automatically discover and register functions from tools modules"""
    registry = {}
    modules = _discover_mcp_tool_modules()

    for module in modules:
        module_name = module.__name__.split(".")[-1]

        for name, obj in inspect.getmembers(module):
            if _is_valid_function(obj, name):
                try:
                    registry[name] = extract_function_metadata(obj)
                    logger.info(f"Registered function: {name} from {module_name}")
                except Exception:
                    logger.exception(f"Failed to register function {name}")
                    # Don't raise - continue with other functions

    return registry


def get_function_registry() -> dict[str, dict[str, Any]]:
    """Get the function registry, building it if needed"""
    return build_function_registry()


# For compatibility, expose the registry
FUNCTION_REGISTRY = get_function_registry()

