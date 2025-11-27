# MCP Write Server

A **NON-OFFICIAL** write-enabled extension of the official Braze MCP server, designed for Solution Engineers to create demos, trigger campaigns, and manage test environments.

## ⚠️ Important Safety Notice

This server enables **WRITE OPERATIONS** to your Braze workspace. It includes multiple safety mechanisms:

- **Workspace validation**: Only works with demo/POC/test workspaces by default
- **Rate limiting**: Prevents accidental spam
- **Dry run mode**: Test operations without making changes
- **Confirmation requirements**: Destructive operations need explicit confirmation
- **Production blocking**: Prevents writes to production workspaces unless explicitly enabled

## Features

### Write Operations
- ✅ User profile management (attributes, events, purchases)
- ✅ Campaign triggering and management
- ✅ Canvas triggering and management
- ✅ Catalog item management
- ✅ Content block management
- ✅ User deletion and identification

### Safety Features
- ✅ Environment-based workspace validation
- ✅ Rate limiting per operation type
- ✅ Dry run mode for all operations
- ✅ Confirmation requirements for destructive operations
- ✅ Comprehensive logging and audit trail

## Installation

```bash
pip install -e .
```

Or with uv:

```bash
uv pip install -e .
```

## Configuration

### Environment Variables

```bash
# Required
BRAZE_API_KEY=your-api-key-here
BRAZE_BASE_URL=https://rest.iad-01.braze.com

# Safety Configuration
BRAZE_WRITE_ENABLED=true                    # Enable write operations
BRAZE_ALLOW_PRODUCTION=false                # Block production workspaces
BRAZE_ALLOWED_WORKSPACES=demo-,poc-,test-  # Allowed workspace patterns
BRAZE_DRY_RUN_DEFAULT=false                 # Default dry run mode

# Rate Limits
BRAZE_MAX_SENDS_PER_HOUR=1000              # Max campaign/canvas sends per hour
BRAZE_MAX_CATALOG_UPDATES_PER_MIN=100      # Max catalog updates per minute
```

### MCP Client Configuration

Add to your MCP client configuration (e.g., Claude Desktop):

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

## Usage Examples

### Update User Attributes

```python
await update_user_attributes(
    ctx,
    external_id="user_12345",
    attributes={
        "first_name": "John",
        "last_name": "Doe",
        "email": "[email protected]",
        "subscription_tier": "premium"
    }
)
```

### Track Custom Event

```python
await track_event(
    ctx,
    event_name="completed_tutorial",
    external_id="user_12345",
    properties={
        "tutorial_name": "Getting Started",
        "completion_time_seconds": 180
    }
)
```

### Send Campaign

```python
await send_campaign(
    ctx,
    campaign_id="your-campaign-id",
    recipients=[{
        "external_user_id": "user_12345"
    }]
)
```

### Trigger Canvas

```python
await trigger_canvas(
    ctx,
    canvas_id="your-canvas-id",
    recipients=[{
        "external_user_id": "user_12345"
    }],
    canvas_entry_properties={
        "promo_code": "DEMO2024"
    }
)
```

### Dry Run Mode

Test any operation without making changes:

```python
result = await update_user_attributes(
    ctx,
    external_id="user_12345",
    attributes={"test_field": "test_value"},
    dry_run=True  # No actual API call made
)
```

## Architecture

```
braze_mcp_write/
├── models/              # Pydantic models for validation
│   ├── errors.py
│   └── responses.py
├── tools/               # MCP tool implementations
│   ├── users_write.py   # User tracking operations
│   ├── campaigns_write.py
│   ├── canvas_write.py
│   ├── catalogs_write.py
│   └── content_blocks_write.py
├── utils/               # Utilities
│   ├── context.py       # Context management
│   ├── http.py          # HTTP client
│   ├── logging.py       # Logging setup
│   └── safety.py        # Safety mechanisms
├── registry_builder.py  # Auto-discovery system
├── server.py            # FastMCP server
└── main.py              # Entry point
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
ruff check .
```

## Safety Best Practices

1. **Always use demo workspaces**: Set up dedicated demo workspaces with the "demo-", "poc-", or "test-" prefix in the URL
2. **Test with dry run first**: Use `dry_run=True` to validate operations before execution
3. **Monitor rate limits**: Be aware of Braze API rate limits for your workspace
4. **Use confirmation for destructive ops**: Operations like `delete_user` require `confirm=True`
5. **Review logs**: Check logs regularly for unexpected behavior

## Differences from Official Braze MCP

This server extends the official read-only Braze MCP server with:
- Write operations for campaigns, canvas, users, catalogs, and content blocks
- Comprehensive safety mechanisms to prevent accidental production writes
- Rate limiting to prevent API abuse
- Dry run mode for testing
- Enhanced logging and audit trails

## License

MIT License - See LICENSE file for details

## Disclaimer

This is a developer tool for creating demos and POCs. Use with caution and always verify your workspace configuration before enabling write operations.

