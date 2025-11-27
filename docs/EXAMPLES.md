# Example Usage Scenarios

This document provides practical examples for common use cases with the Braze MCP Write Server.

## User Management

### Creating and Updating User Profiles

#### Simple Profile Update

```python
call_function(
    function_name="update_user_attributes",
    parameters={
        "external_id": "demo_user_001",
        "attributes": {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "[email protected]",
            "phone": "+1234567890",
            "subscription_tier": "premium",
            "account_created": "2024-11-28T10:00:00Z"
        }
    }
)
```

#### Update Multiple Custom Attributes

```python
call_function(
    function_name="update_user_attributes",
    parameters={
        "external_id": "demo_user_001",
        "attributes": {
            "loyalty_points": 1500,
            "vip_status": true,
            "favorite_categories": ["electronics", "books", "home"],
            "last_purchase_date": "2024-11-20",
            "preferences": {
                "email_frequency": "weekly",
                "sms_enabled": true
            }
        }
    }
)
```

### Event Tracking

#### Track Custom Event

```python
call_function(
    function_name="track_event",
    parameters={
        "event_name": "product_viewed",
        "external_id": "demo_user_001",
        "properties": {
            "product_id": "PROD-12345",
            "product_name": "Wireless Headphones",
            "category": "electronics",
            "price": 99.99,
            "view_duration_seconds": 45
        }
    }
)
```

#### Track Multiple Events for Different Users

```python
# Use track_user_data for batch operations
call_function(
    function_name="track_user_data",
    parameters={
        "events": [
            {
                "external_id": "demo_user_001",
                "name": "button_clicked",
                "properties": {
                    "button_name": "add_to_cart",
                    "page": "product_detail"
                }
            },
            {
                "external_id": "demo_user_002",
                "name": "page_viewed",
                "properties": {
                    "page_name": "checkout",
                    "referrer": "product_page"
                }
            }
        ]
    }
)
```

### Purchase Tracking

#### Track Single Purchase

```python
call_function(
    function_name="track_purchase",
    parameters={
        "external_id": "demo_user_001",
        "product_id": "SKU-HEADPHONES-001",
        "currency": "USD",
        "price": 99.99,
        "quantity": 1,
        "properties": {
            "category": "electronics",
            "brand": "AudioTech",
            "discount_applied": true,
            "discount_code": "WINTER20",
            "final_price": 79.99
        }
    }
)
```

#### Batch Update: Attributes, Events, and Purchases

```python
call_function(
    function_name="track_user_data",
    parameters={
        "attributes": [
            {
                "external_id": "demo_user_001",
                "last_purchase_date": "2024-11-28",
                "total_purchases": 15,
                "lifetime_value": 1499.85
            }
        ],
        "events": [
            {
                "external_id": "demo_user_001",
                "name": "purchase_completed",
                "properties": {
                    "order_id": "ORD-2024-1128-001",
                    "total_items": 3
                }
            }
        ],
        "purchases": [
            {
                "external_id": "demo_user_001",
                "product_id": "SKU-HEADPHONES-001",
                "currency": "USD",
                "price": 79.99
            }
        ]
    }
)
```

## Campaign Management

### Sending Campaigns

#### Send to Specific Users

```python
call_function(
    function_name="send_campaign",
    parameters={
        "campaign_id": "your-campaign-id-here",
        "recipients": [
            {
                "external_user_id": "demo_user_001",
                "trigger_properties": {
                    "promo_code": "DEMO2024",
                    "discount_amount": 20,
                    "expiry_date": "2024-12-31"
                }
            },
            {
                "external_user_id": "demo_user_002",
                "trigger_properties": {
                    "promo_code": "VIP2024",
                    "discount_amount": 30,
                    "expiry_date": "2024-12-31"
                }
            }
        ]
    }
)
```

#### Test Campaign with Dry Run

```python
call_function(
    function_name="send_campaign",
    parameters={
        "campaign_id": "your-campaign-id-here",
        "recipients": [
            {
                "external_user_id": "demo_user_001"
            }
        ],
        "dry_run": true
    }
)
```

#### Schedule Campaign for Later

```python
call_function(
    function_name="schedule_campaign",
    parameters={
        "campaign_id": "your-campaign-id-here",
        "send_at": "2024-12-01T09:00:00Z",
        "recipients": [
            {
                "external_user_id": "demo_user_001"
            }
        ]
    }
)
```

## Canvas Management

### Triggering Canvas Flows

#### Trigger Canvas Entry

```python
call_function(
    function_name="trigger_canvas",
    parameters={
        "canvas_id": "your-canvas-id-here",
        "recipients": [
            {
                "external_user_id": "demo_user_001",
                "canvas_entry_properties": {
                    "onboarding_source": "website",
                    "signup_date": "2024-11-28",
                    "initial_product_interest": "premium_plan"
                }
            }
        ]
    }
)
```

#### Trigger Canvas with Multiple Recipients

```python
call_function(
    function_name="trigger_canvas",
    parameters={
        "canvas_id": "your-canvas-id-here",
        "recipients": [
            {
                "external_user_id": "demo_user_001"
            },
            {
                "external_user_id": "demo_user_002"
            },
            {
                "external_user_id": "demo_user_003"
            }
        ],
        "canvas_entry_properties": {
            "campaign_type": "reengagement",
            "offer_type": "special_promotion"
        }
    }
)
```

## Catalog Management

### Managing Catalog Items

#### Create Catalog Items

```python
call_function(
    function_name="create_catalog_items",
    parameters={
        "catalog_name": "products",
        "items": [
            {
                "id": "PROD-001",
                "name": "Wireless Headphones",
                "price": 99.99,
                "category": "electronics",
                "in_stock": true,
                "image_url": "https://example.com/images/headphones.jpg",
                "rating": 4.5
            },
            {
                "id": "PROD-002",
                "name": "Smart Watch",
                "price": 299.99,
                "category": "electronics",
                "in_stock": true,
                "image_url": "https://example.com/images/watch.jpg",
                "rating": 4.8
            }
        ]
    }
)
```

#### Update Catalog Items

```python
call_function(
    function_name="update_catalog_items",
    parameters={
        "catalog_name": "products",
        "items": [
            {
                "id": "PROD-001",
                "price": 89.99,
                "in_stock": false
            }
        ]
    }
)
```

#### Delete Catalog Items

```python
call_function(
    function_name="delete_catalog_items",
    parameters={
        "catalog_name": "products",
        "item_ids": ["PROD-001", "PROD-002"],
        "confirm": true
    }
)
```

### Creating Catalogs

```python
call_function(
    function_name="create_catalog",
    parameters={
        "name": "demo_products",
        "description": "Demo product catalog for testing",
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "price", "type": "number"},
            {"name": "category", "type": "string"},
            {"name": "in_stock", "type": "boolean"},
            {"name": "last_updated", "type": "time"}
        ]
    }
)
```

## Content Block Management

### Creating and Updating Content Blocks

#### Create HTML Content Block

```python
call_function(
    function_name="create_content_block",
    parameters={
        "name": "promo_banner",
        "content": "<div style='background: #ff6b6b; padding: 20px;'><h2>Special Offer!</h2><p>Get 20% off with code DEMO2024</p></div>",
        "description": "Promotional banner for campaigns",
        "content_type": "html",
        "tags": ["promotion", "banner", "demo"]
    }
)
```

#### Update Content Block

```python
call_function(
    function_name="update_content_block",
    parameters={
        "content_block_id": "your-content-block-id",
        "content": "<div style='background: #4ecdc4; padding: 20px;'><h2>New Offer!</h2><p>Get 30% off with code VIP2024</p></div>",
        "description": "Updated promotional banner"
    }
)
```

## Advanced Scenarios

### Demo Setup: Complete User Journey

```python
# 1. Create user profile
call_function(
    function_name="update_user_attributes",
    parameters={
        "external_id": "demo_journey_user",
        "attributes": {
            "first_name": "Demo",
            "last_name": "User",
            "email": "[email protected]",
            "signup_date": "2024-11-28"
        }
    }
)

# 2. Track signup event
call_function(
    function_name="track_event",
    parameters={
        "event_name": "account_created",
        "external_id": "demo_journey_user",
        "properties": {
            "source": "demo",
            "plan": "free"
        }
    }
)

# 3. Trigger welcome canvas
call_function(
    function_name="trigger_canvas",
    parameters={
        "canvas_id": "welcome-canvas-id",
        "recipients": [
            {
                "external_user_id": "demo_journey_user",
                "canvas_entry_properties": {
                    "onboarding_type": "self_serve"
                }
            }
        ]
    }
)

# 4. Simulate product interest
call_function(
    function_name="track_event",
    parameters={
        "event_name": "product_viewed",
        "external_id": "demo_journey_user",
        "properties": {
            "product_id": "PROD-PREMIUM",
            "category": "subscription"
        }
    }
)

# 5. Send targeted campaign
call_function(
    function_name="send_campaign",
    parameters={
        "campaign_id": "upgrade-campaign-id",
        "recipients": [
            {
                "external_user_id": "demo_journey_user",
                "trigger_properties": {
                    "discount": 25,
                    "trial_days": 30
                }
            }
        ]
    }
)
```

### Cleanup After Demo

```python
# Delete test user
call_function(
    function_name="delete_user",
    parameters={
        "external_id": "demo_journey_user",
        "confirm": true
    }
)
```

## Tips for Demos

1. **Always use dry_run first**: Test operations without making changes
2. **Use descriptive IDs**: Make demo user IDs clearly identifiable (e.g., `demo_user_001`)
3. **Tag demo content**: Use tags like "demo" or "test" for easy identification
4. **Clean up after**: Delete demo users and data when done
5. **Use consistent data**: Create realistic but consistent demo data
6. **Leverage catalogs**: Use catalogs for dynamic demo content
7. **Test error scenarios**: Show both success and error handling

## Common Patterns

### Pattern: Abandoned Cart Recovery

```python
# 1. Track cart abandonment
call_function(
    function_name="track_event",
    parameters={
        "event_name": "cart_abandoned",
        "external_id": "user_123",
        "properties": {
            "cart_value": 149.99,
            "items_count": 3,
            "abandonment_time": "2024-11-28T14:30:00Z"
        }
    }
)

# 2. Trigger recovery canvas
call_function(
    function_name="trigger_canvas",
    parameters={
        "canvas_id": "cart-recovery-canvas",
        "recipients": [
            {
                "external_user_id": "user_123",
                "canvas_entry_properties": {
                    "cart_value": 149.99,
                    "discount_offer": 10
                }
            }
        ]
    }
)
```

### Pattern: Post-Purchase Engagement

```python
# Track purchase and trigger follow-up
call_function(
    function_name="track_user_data",
    parameters={
        "purchases": [
            {
                "external_id": "user_123",
                "product_id": "PROD-001",
                "currency": "USD",
                "price": 99.99
            }
        ],
        "events": [
            {
                "external_id": "user_123",
                "name": "purchase_completed",
                "properties": {
                    "order_id": "ORD-001",
                    "first_purchase": true
                }
            }
        ],
        "attributes": [
            {
                "external_id": "user_123",
                "last_purchase_date": "2024-11-28",
                "customer_tier": "silver"
            }
        ]
    }
)

# Then trigger thank you canvas
call_function(
    function_name="trigger_canvas",
    parameters={
        "canvas_id": "post-purchase-canvas",
        "recipients": [
            {
                "external_user_id": "user_123"
            }
        ]
    }
)
```

