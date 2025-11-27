# Changelog

All notable changes to the Braze MCP Write Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-11-28

### Added
- Initial release of Braze MCP Write Server
- Core server infrastructure with FastMCP
- Auto-discovery registry system for tools
- Comprehensive safety mechanisms:
  - Workspace validation with URL pattern matching
  - Global write enable/disable toggle
  - Dry run mode for all operations
  - Confirmation requirements for destructive operations
  - Rate limiting per operation type
- User management operations (6 functions):
  - `track_user_data` - Batch track attributes, events, purchases
  - `update_user_attributes` - Update user profiles
  - `track_event` - Track custom events
  - `track_purchase` - Track purchases
  - `delete_user` - Delete users (with confirmation)
  - `identify_users` - Merge user profiles
- Campaign operations (4 functions):
  - `send_campaign` - Send campaigns immediately
  - `schedule_campaign` - Schedule campaigns
  - `update_campaign_schedule` - Update scheduled campaigns
  - `delete_scheduled_campaign` - Cancel scheduled campaigns
- Canvas operations (4 functions):
  - `trigger_canvas` - Trigger Canvas flows
  - `schedule_canvas` - Schedule Canvas triggers
  - `update_canvas_schedule` - Update scheduled Canvas
  - `delete_scheduled_canvas` - Cancel scheduled Canvas
- Catalog management (5 functions):
  - `create_catalog_items` - Add items to catalogs
  - `update_catalog_items` - Update catalog items
  - `delete_catalog_items` - Remove catalog items
  - `create_catalog` - Create new catalogs
  - `delete_catalog` - Delete catalogs
- Content block operations (2 functions):
  - `create_content_block` - Create reusable content
  - `update_content_block` - Update content blocks
- Comprehensive documentation:
  - README with feature overview
  - QUICKSTART for 5-minute setup
  - GETTING_STARTED with detailed instructions
  - EXAMPLES with practical use cases
  - SAFETY best practices guide
  - ARCHITECTURE diagram and flow
  - PROJECT_SUMMARY with complete overview
- Configuration management:
  - Environment variable support
  - Example configuration file
  - MCP client configuration templates
- Error handling and logging:
  - Structured error responses
  - Comprehensive logging
  - Audit trail support

### Security
- Multi-layer safety system to prevent production writes
- Workspace URL validation
- Explicit confirmation for destructive operations
- Rate limiting to prevent API abuse
- Dry run mode for testing

## [Unreleased]

### Planned
- Segment management operations
- SMS/push token management
- Subscription group updates
- Email template management
- Enhanced analytics and reporting
- Web dashboard for monitoring
- Interactive CLI tool
- Unit and integration tests
- Performance optimizations
- Additional safety features

### Under Consideration
- Rollback capabilities
- Per-user rate limits
- Integration with monitoring systems
- Pre-commit hooks for safety checks
- Better error messages with AI-powered suggestions

---

## Version History

- **0.1.0** (2024-11-28): Initial release with core functionality

## Upgrade Guide

### From Nothing to 0.1.0

This is the initial release. Follow the QUICKSTART.md guide to set up.

## Breaking Changes

None yet - this is the initial release.

## Deprecations

None yet - this is the initial release.

## Support

For questions about changes or upgrades:
1. Check the documentation in `docs/`
2. Review the PROJECT_SUMMARY.md
3. Consult the QUICKSTART.md for setup

## Contributing

When adding new features or changes:
1. Update this CHANGELOG.md
2. Follow semantic versioning
3. Update documentation
4. Add examples if applicable
5. Update tests

## Links

- [Official Braze MCP](https://pypi.org/project/braze-mcp-server/)
- [Braze API Documentation](https://www.braze.com/docs/api/basics/)
- [MCP Protocol](https://modelcontextprotocol.io/)

