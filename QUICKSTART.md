# Quick Start Guide

Get up and running with the Braze MCP Write Server in 5 minutes!

## 1. Install Dependencies

```bash
cd "/Users/saarkia/Documents/Coding/AR Braze MCP"

# Install the package
pip install -e .

# Or with uv (recommended)
uv pip install -e .
```

## 2. Configure Environment

Copy the example environment file:

```bash
cp env.example .env
```

Edit `.env` and add your Braze credentials:

```bash
BRAZE_API_KEY=your-api-key-here
BRAZE_BASE_URL=https://rest.demo-01.braze.com  # Use your demo workspace
BRAZE_WRITE_ENABLED=true
```

## 3. Configure MCP Client

Add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "braze-write": {
      "command": "python",
      "args": ["-m", "braze_mcp_write.main"],
      "env": {
        "BRAZE_API_KEY": "your-api-key",
        "BRAZE_BASE_URL": "https://rest.demo-01.braze.com",
        "BRAZE_WRITE_ENABLED": "true",
        "BRAZE_ALLOWED_WORKSPACES": "demo-,poc-,test-"
      }
    }
  }
}
```

## 4. Test the Server

Restart Claude Desktop and test:

```
list_functions()
```

You should see all available functions!

## 5. Try Your First Write Operation

Test with dry run first:

```
call_function(
    function_name="update_user_attributes",
    parameters={
        "external_id": "demo_user_test",
        "attributes": {
            "first_name": "Test",
            "demo": true
        },
        "dry_run": true
    }
)
```

Then execute for real:

```
call_function(
    function_name="update_user_attributes",
    parameters={
        "external_id": "demo_user_test",
        "attributes": {
            "first_name": "Test",
            "demo": true
        }
    }
)
```

## Next Steps

- Read the [Getting Started Guide](docs/GETTING_STARTED.md) for detailed setup
- Check out [Examples](docs/EXAMPLES.md) for common use cases
- Review [Safety Best Practices](docs/SAFETY.md) before using in demos

## Available Operations

### User Management
- `update_user_attributes` - Update user profiles
- `track_event` - Track custom events
- `track_purchase` - Track purchases
- `delete_user` - Delete users
- `identify_users` - Merge user profiles

### Campaigns
- `send_campaign` - Send campaigns immediately
- `schedule_campaign` - Schedule campaigns
- `update_campaign_schedule` - Update scheduled campaigns
- `delete_scheduled_campaign` - Cancel scheduled campaigns

### Canvas
- `trigger_canvas` - Trigger Canvas flows
- `schedule_canvas` - Schedule Canvas triggers
- `update_canvas_schedule` - Update scheduled Canvas
- `delete_scheduled_canvas` - Cancel scheduled Canvas

### Catalogs
- `create_catalog_items` - Add items to catalogs
- `update_catalog_items` - Update catalog items
- `delete_catalog_items` - Remove catalog items
- `create_catalog` - Create new catalogs
- `delete_catalog` - Delete catalogs

### Content Blocks
- `create_content_block` - Create reusable content
- `update_content_block` - Update content blocks

## Troubleshooting

### "Write operations are disabled"
Solution: Set `BRAZE_WRITE_ENABLED=true` in your environment

### "Write operation blocked for workspace"
Solution: Use a demo/test workspace with URL containing "demo-", "poc-", or "test-"

### "Import mcp.server.fastmcp could not be resolved"
Solution: Install dependencies with `pip install -e .`

### Server not showing in Claude
Solution: 
1. Check configuration file syntax (valid JSON)
2. Restart Claude Desktop
3. Check Claude logs for errors

## Support

- Documentation: See `docs/` folder
- Examples: See `docs/EXAMPLES.md`
- Safety: See `docs/SAFETY.md`

