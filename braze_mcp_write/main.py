"""
Main entry point for Braze MCP Write Server.
"""

import sys

from braze_mcp_write.server import mcp
from braze_mcp_write.utils.logging import configure_logging, get_logger

logger = get_logger(__name__)


def main():
    """Main entry point for the server."""
    configure_logging()
    
    logger.info("Starting Braze MCP Write Server")
    
    try:
        # Run the FastMCP server
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

