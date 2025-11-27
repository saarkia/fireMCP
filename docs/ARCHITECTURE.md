# Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MCP Client (Claude)                          │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ MCP Protocol
                                 │
┌────────────────────────────────▼────────────────────────────────────┐
│                      FastMCP Server (server.py)                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Tools:                                                        │  │
│  │  - list_functions()                                           │  │
│  │  - call_function(function_name, parameters)                   │  │
│  └───────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────┐
│                   Registry Builder (registry_builder.py)             │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Auto-discovery:                                              │  │
│  │  - Scans tools/ directory                                     │  │
│  │  - Finds modules with __register_mcp_tools__ = True          │  │
│  │  - Extracts metadata from docstrings                         │  │
│  │  - Builds function registry                                   │  │
│  └───────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────┐
│                         Tools Layer (tools/)                         │
│  ┌──────────────────┬──────────────────┬──────────────────────┐    │
│  │ users_write.py   │ campaigns_write  │ canvas_write.py      │    │
│  │ - track_user_data│ - send_campaign  │ - trigger_canvas     │    │
│  │ - update_user    │ - schedule       │ - schedule_canvas    │    │
│  │ - track_event    │ - update         │ - update_schedule    │    │
│  │ - track_purchase │ - delete         │ - delete             │    │
│  │ - delete_user    │                  │                      │    │
│  │ - identify_users │                  │                      │    │
│  └──────────────────┴──────────────────┴──────────────────────┘    │
│  ┌──────────────────┬──────────────────────────────────────────┐   │
│  │ catalogs_write   │ content_blocks_write.py                  │   │
│  │ - create_items   │ - create_content_block                   │   │
│  │ - update_items   │ - update_content_block                   │   │
│  │ - delete_items   │                                          │   │
│  │ - create_catalog │                                          │   │
│  │ - delete_catalog │                                          │   │
│  └──────────────────┴──────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────┐
│                       Safety Layer (utils/safety.py)                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Safety Mechanisms:                                           │  │
│  │  1. validate_write_enabled()   - Global write toggle         │  │
│  │  2. validate_workspace_safety()- URL pattern matching        │  │
│  │  3. supports_dry_run()         - Test without executing      │  │
│  │  4. require_confirmation()     - Destructive op protection   │  │
│  │  5. rate_limit()               - Prevent API abuse           │  │
│  └───────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────┐
│                     Core Utilities (utils/)                          │
│  ┌──────────────────┬──────────────────┬──────────────────────┐    │
│  │ context.py       │ http.py          │ logging.py           │    │
│  │ - BrazeContext   │ - make_request   │ - get_logger         │    │
│  │ - braze_lifespan │ - handle_response│ - configure_logging  │    │
│  │ - get_context    │                  │                      │    │
│  └──────────────────┴──────────────────┴──────────────────────┘    │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ HTTPX AsyncClient
                                 │
┌────────────────────────────────▼────────────────────────────────────┐
│                         Braze REST API                               │
│                     (https://rest.*.braze.com)                       │
└──────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        Configuration Flow                            │
└─────────────────────────────────────────────────────────────────────┘

Environment Variables              Context Initialization
┌──────────────────┐              ┌──────────────────────┐
│ BRAZE_API_KEY    │──────────────>│ BrazeContext:        │
│ BRAZE_BASE_URL   │              │ - api_key            │
│ BRAZE_WRITE_*    │──────────────>│ - base_url           │
└──────────────────┘              │ - http_client        │
                                  └──────────────────────┘
                                            │
                                            │ Passed to
                                            ▼
                                  ┌──────────────────────┐
                                  │ All Tool Functions   │
                                  │ via ctx parameter    │
                                  └──────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         Request Flow                                 │
└─────────────────────────────────────────────────────────────────────┘

1. Claude sends MCP request
        │
        ▼
2. FastMCP server receives call_function()
        │
        ▼
3. Registry lookup finds implementation
        │
        ▼
4. Safety decorators execute (in order):
   a. validate_write_enabled()
   b. validate_workspace_safety()
   c. require_confirmation() [if applicable]
   d. rate_limit() [if applicable]
   e. supports_dry_run()
        │
        ▼
5. If dry_run=True: Return preview, STOP
   If dry_run=False: Continue
        │
        ▼
6. Tool function executes
   - Builds request body
   - Calls make_request()
        │
        ▼
7. HTTP client sends to Braze API
        │
        ▼
8. handle_response() processes result
        │
        ▼
9. Return result to Claude

┌─────────────────────────────────────────────────────────────────────┐
│                      Safety Decision Tree                            │
└─────────────────────────────────────────────────────────────────────┘

Write operation requested
        │
        ▼
   BRAZE_WRITE_ENABLED=true?
        │
    ┌───┴───┐
  NO│       │YES
    │       ▼
    │   Workspace URL matches allowed patterns?
    │       │
    │   ┌───┴───┐
    │ NO│       │YES
    │   │       ▼
    │   │   Destructive operation?
    │   │       │
    │   │   ┌───┴───┐
    │   │ YES       │NO
    │   │   │       │
    │   │   ▼       │
    │   │ confirm=True?  │
    │   │   │       │
    │   │ ┌─┴─┐     │
    │   │NO  YES    │
    │   │ │   │     │
    │   │ ▼   │     │
    │   │BLOCK│     │
    │   │     ▼     ▼
    │   │   dry_run=True?
    │   │       │
    │   │   ┌───┴───┐
    │   │ YES       │NO
    │   │   │       │
    │   │   ▼       ▼
    │   │PREVIEW  EXECUTE
    │   │
    ▼   ▼
  ERROR: Operation blocked

