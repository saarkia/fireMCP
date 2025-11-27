# Getting Started with Braze MCP Write Server

This guide will help you set up and start using the Braze MCP Write Server.

## Prerequisites

- Python 3.10 or higher
- A Braze workspace (preferably a demo/test workspace)
- Braze REST API key with appropriate permissions
- Your Braze REST API endpoint URL

## Installation

### Option 1: Install from source (Development)

```bash
# Clone or navigate to the repository
cd "AR Braze MCP"

# Install in editable mode
pip install -e .

# Or with uv (recommended)
uv pip install -e .
```

### Option 2: Install as package

```bash
pip install .
```

## Configuration

### 1. Get Your Braze Credentials

You'll need two pieces of information:

1. **API Key**: Found in Braze Dashboard → Settings → API Keys
   - Create a new API key with appropriate permissions for write operations
   - Required permissions: users.track, campaigns.trigger.send, canvas.trigger.send, catalogs.*, content_blocks.*

2. **REST Endpoint**: Your Braze REST API endpoint (e.g., `https://rest.iad-01.braze.com`)
   - Found in Braze Dashboard → Settings → API Settings

### 2. Set Environment Variables

Create a `.env` file or export environment variables:

```bash
# Required
export BRAZE_API_KEY="your-api-key-here"
export BRAZE_BASE_URL="https://rest.iad-01.braze.com"

# Safety Configuration
export BRAZE_WRITE_ENABLED="true"
export BRAZE_ALLOW_PRODUCTION="false"
export BRAZE_ALLOWED_WORKSPACES="demo-,poc-,test-"

# Optional: Rate Limits
export BRAZE_MAX_SENDS_PER_HOUR="1000"
export BRAZE_MAX_CATALOG_UPDATES_PER_MIN="100"
```

### 3. Configure Your MCP Client

For Claude Desktop, edit your configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the server configuration:

```json
{
  "mcpServers": {
    "braze-write": {
      "command": "python",
      "args": ["-m", "braze_mcp_write.main"],
      "env": {
        "BRAZE_API_KEY": "your-api-key",
        "BRAZE_BASE_URL": "https://rest.iad-01.braze.com",
        "BRAZE_WRITE_ENABLED": "true",
        "BRAZE_ALLOWED_WORKSPACES": "demo-,poc-,test-"
      }
    }
  }
}
```

## Testing Your Setup

### 1. Test Basic Connectivity

Start a Python shell and test the server:

```python
import asyncio
from braze_mcp_write.utils import BrazeContext
import httpx
import os

async def test_connection():
    api_key = os.getenv("BRAZE_API_KEY")
    base_url = os.getenv("BRAZE_BASE_URL")
    
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {api_key}"}
    ) as client:
        response = await client.get(f"{base_url}/campaigns/list")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

asyncio.run(test_connection())
```

### 2. Test with Dry Run

Use dry run mode to test operations without making actual changes:

```python
# In Claude or your MCP client, try:
call_function(
    function_name="update_user_attributes",
    parameters={
        "external_id": "test_user_123",
        "attributes": {
            "first_name": "Test",
            "last_name": "User"
        },
        "dry_run": true
    }
)
```

## Common Tasks

### List Available Functions

```
list_functions()
```

### Update a User Profile

```python
call_function(
    function_name="update_user_attributes",
    parameters={
        "external_id": "user_12345",
        "attributes": {
            "first_name": "John",
            "email": "[email protected]",
            "custom_field": "custom_value"
        }
    }
)
```

### Track a Custom Event

```python
call_function(
    function_name="track_event",
    parameters={
        "event_name": "demo_event",
        "external_id": "user_12345",
        "properties": {
            "event_property": "value"
        }
    }
)
```

### Send a Campaign

```python
call_function(
    function_name="send_campaign",
    parameters={
        "campaign_id": "your-campaign-id",
        "recipients": [
            {
                "external_user_id": "user_12345",
                "trigger_properties": {
                    "promo_code": "DEMO2024"
                }
            }
        ]
    }
)
```

### Trigger a Canvas

```python
call_function(
    function_name="trigger_canvas",
    parameters={
        "canvas_id": "your-canvas-id",
        "recipients": [
            {
                "external_user_id": "user_12345"
            }
        ],
        "canvas_entry_properties": {
            "entry_property": "value"
        }
    }
)
```

## Safety Features

### Workspace Validation

By default, the server only allows writes to workspaces with URLs containing:
- `demo-`
- `poc-`
- `test-`

To override this (not recommended for production):
```bash
export BRAZE_ALLOW_PRODUCTION="true"
```

### Dry Run Mode

Test any operation without making changes:
```python
parameters={
    "dry_run": true,
    # ... other parameters
}
```

### Confirmation for Destructive Operations

Operations like `delete_user` or `delete_catalog` require explicit confirmation:
```python
parameters={
    "confirm": true,
    # ... other parameters
}
```

## Troubleshooting

### Error: "Write operations are disabled"

Make sure `BRAZE_WRITE_ENABLED=true` is set in your environment.

### Error: "Write operation blocked for workspace"

Your workspace URL doesn't match the allowed patterns. Either:
1. Use a demo/test workspace
2. Update `BRAZE_ALLOWED_WORKSPACES` to include your workspace pattern
3. Set `BRAZE_ALLOW_PRODUCTION=true` (not recommended)

### Error: "Rate limit exceeded"

You've hit the configured rate limit. Wait for the time window to pass or adjust the rate limit settings.

### Connection Issues

1. Verify your API key has the correct permissions
2. Check that your REST endpoint URL is correct
3. Ensure you have network connectivity to Braze

## Next Steps

- Review the [API Reference](API_REFERENCE.md) for detailed function documentation
- Check out [Examples](EXAMPLES.md) for common use cases
- Read about [Safety Best Practices](SAFETY.md)

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Review the safety documentation
3. Consult the Braze API documentation
4. Open an issue in the repository

