# Safety Best Practices

The Braze MCP Write Server includes multiple safety mechanisms to prevent accidental damage to production workspaces. This guide covers how to use them effectively.

## Core Safety Principles

1. **Always use demo/test workspaces** for this server
2. **Never bypass safety checks** in production environments
3. **Test with dry run first** before executing write operations
4. **Monitor rate limits** to avoid API throttling
5. **Clean up demo data** after testing

## Safety Mechanisms

### 1. Workspace Validation

The server validates that write operations only occur in approved workspaces.

#### How it Works

By default, only workspaces with URLs containing these patterns are allowed:
- `demo-`
- `poc-`
- `test-`

Example allowed URLs:
- `https://rest.demo-01.braze.com`
- `https://rest.poc-iad-01.braze.com`
- `https://rest.test-eu.braze.com`

#### Configuration

```bash
# Set allowed workspace patterns (comma-separated)
export BRAZE_ALLOWED_WORKSPACES="demo-,poc-,test-,staging-"

# Override to allow ANY workspace (DANGEROUS - not recommended)
export BRAZE_ALLOW_PRODUCTION="true"
```

#### What Happens When Blocked

```json
{
  "error": "Write operation blocked",
  "workspace": "https://rest.iad-01.braze.com",
  "message": "Only workspaces matching these patterns are allowed: ['demo-', 'poc-', 'test-']",
  "solution": "Use a demo workspace or update BRAZE_ALLOWED_WORKSPACES"
}
```

### 2. Write Operations Toggle

All write operations can be globally disabled.

#### Configuration

```bash
# Enable write operations (required)
export BRAZE_WRITE_ENABLED="true"

# Disable write operations (read-only mode)
export BRAZE_WRITE_ENABLED="false"
```

When disabled, all write operations will fail with:
```json
{
  "error": "Write operations are disabled",
  "message": "Set BRAZE_WRITE_ENABLED=true to enable"
}
```

### 3. Dry Run Mode

Test operations without making actual API calls.

#### Usage

Add `dry_run: true` to any write operation:

```python
call_function(
    function_name="update_user_attributes",
    parameters={
        "external_id": "test_user",
        "attributes": {"first_name": "Test"},
        "dry_run": true  # No actual API call
    }
)
```

#### Response Format

```json
{
  "dry_run": true,
  "operation": "update_user_attributes",
  "would_execute": {
    "function": "update_user_attributes",
    "args": [],
    "kwargs": {
      "external_id": "test_user",
      "attributes": {"first_name": "Test"}
    }
  },
  "message": "This is a dry run. No actual API call was made."
}
```

#### Default Dry Run

Set dry run as the default for all operations:

```bash
export BRAZE_DRY_RUN_DEFAULT="true"
```

Then explicitly set `dry_run: false` when you want to execute:

```python
parameters={
    # ... your parameters
    "dry_run": false  # Actually execute
}
```

### 4. Confirmation for Destructive Operations

Certain operations require explicit confirmation.

#### Operations Requiring Confirmation

- `delete_user`
- `delete_catalog`
- `delete_catalog_items`
- `delete_scheduled_campaign`
- `delete_scheduled_canvas`

#### Usage

Add `confirm: true` to proceed:

```python
call_function(
    function_name="delete_user",
    parameters={
        "external_id": "demo_user_001",
        "confirm": true  # Required
    }
)
```

#### Without Confirmation

```json
{
  "error": "Confirmation required",
  "operation": "delete_user",
  "message": "Add confirm=True to proceed",
  "parameters": {
    "external_id": "demo_user_001"
  }
}
```

### 5. Rate Limiting

Prevents API abuse and respects Braze rate limits.

#### Default Limits

```bash
# Campaign/Canvas sends
export BRAZE_MAX_SENDS_PER_HOUR="1000"

# Catalog operations
export BRAZE_MAX_CATALOG_UPDATES_PER_MIN="100"
```

#### How it Works

Each operation type is tracked independently:
- Sends (campaigns, canvas): 1000 per hour
- Catalog updates: 100 per minute
- Custom limits can be set per operation

#### When Limit Exceeded

```json
{
  "error": "Rate limit exceeded",
  "operation": "send_campaign",
  "message": "Rate limit exceeded for send_campaign. 1000/1000 requests in window. Try again in 2847 seconds."
}
```

## Recommended Workflow

### 1. Setup Phase

```bash
# Use a dedicated demo workspace
export BRAZE_BASE_URL="https://rest.demo-01.braze.com"

# Enable safety features
export BRAZE_WRITE_ENABLED="true"
export BRAZE_ALLOW_PRODUCTION="false"
export BRAZE_DRY_RUN_DEFAULT="false"
```

### 2. Development/Testing

```python
# Always test with dry run first
call_function(
    function_name="send_campaign",
    parameters={
        "campaign_id": "test-campaign",
        "recipients": [{"external_user_id": "test_user"}],
        "dry_run": true
    }
)

# Verify the dry run response
# Then execute for real
call_function(
    function_name="send_campaign",
    parameters={
        "campaign_id": "test-campaign",
        "recipients": [{"external_user_id": "test_user"}],
        "dry_run": false
    }
)
```

### 3. Demo Presentation

```python
# 1. Create demo users with clear naming
call_function(
    function_name="update_user_attributes",
    parameters={
        "external_id": "demo_presentation_user_001",
        "attributes": {
            "first_name": "Demo",
            "demo_session": "2024-11-28",
            "demo_tag": "presentation"
        }
    }
)

# 2. Perform demo actions
# ...

# 3. Clean up after demo
call_function(
    function_name="delete_user",
    parameters={
        "external_id": "demo_presentation_user_001",
        "confirm": true
    }
)
```

### 4. Cleanup

```python
# Delete test users
call_function(
    function_name="delete_user",
    parameters={
        "external_id": "test_user_001",
        "confirm": true
    }
)

# Delete test catalog items
call_function(
    function_name="delete_catalog_items",
    parameters={
        "catalog_name": "demo_catalog",
        "item_ids": ["DEMO-001", "DEMO-002"],
        "confirm": true
    }
)
```

## Security Checklist

Before going live with the server:

- [ ] Using a dedicated demo/test workspace
- [ ] `BRAZE_WRITE_ENABLED` is set appropriately
- [ ] `BRAZE_ALLOW_PRODUCTION` is `false`
- [ ] API key has minimum required permissions
- [ ] Rate limits are configured
- [ ] Workspace URL patterns are correctly configured
- [ ] Team members understand dry run mode
- [ ] Cleanup procedures are documented

## Emergency Procedures

### If Writes Occur in Wrong Workspace

1. **Immediately disable writes**:
   ```bash
   export BRAZE_WRITE_ENABLED="false"
   ```

2. **Review what was changed**: Check server logs

3. **Contact Braze support** if production data was affected

4. **Update workspace validation**: Add more restrictive patterns

### If Rate Limits are Hit

1. **Wait for the time window to pass**
2. **Review what caused the spike**: Check logs
3. **Adjust rate limits** if legitimate use case
4. **Implement batching** for bulk operations

### If Unauthorized Access Suspected

1. **Rotate API keys immediately**
2. **Disable write operations**
3. **Review access logs**
4. **Update security policies**

## Audit and Logging

The server logs all write operations:

```
2024-11-28 10:30:15 - braze_mcp_write.utils.safety - INFO - Workspace safety check passed for update_user_attributes: https://rest.demo-01.braze.com
2024-11-28 10:30:16 - braze_mcp_write.tools.users_write - INFO - Write operation completed: {'timestamp': '2024-11-28T10:30:16', 'operation': 'update_user_attributes', 'parameters': {...}}
```

### What's Logged

- Timestamp of operation
- Operation name
- Parameters (sanitized)
- Workspace URL
- Success/failure status
- Error details if failed

### Reviewing Logs

```bash
# View recent operations
tail -f /path/to/logs

# Search for specific user
grep "external_id.*user_123" /path/to/logs

# Find failed operations
grep "ERROR" /path/to/logs
```

## Best Practices Summary

1. **Environment Isolation**: Always use separate workspaces for demos
2. **Test First**: Use dry run before every write operation
3. **Explicit Confirmation**: Never automate confirmation for destructive ops
4. **Monitor Usage**: Watch rate limits and API quotas
5. **Clean Up**: Delete demo data after sessions
6. **Document Changes**: Keep records of what was created/modified
7. **Limit Permissions**: Use API keys with minimal required permissions
8. **Regular Audits**: Review logs periodically
9. **Training**: Ensure all users understand safety features
10. **Incident Response**: Have a plan for handling mistakes

## Additional Resources

- [Braze API Rate Limits](https://www.braze.com/docs/api/basics/#rate-limits)
- [Braze API Key Permissions](https://www.braze.com/docs/api/basics/#rest-api-key-permissions)
- [Getting Started Guide](GETTING_STARTED.md)
- [Examples](EXAMPLES.md)

