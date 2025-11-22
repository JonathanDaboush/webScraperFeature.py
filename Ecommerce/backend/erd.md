# E-Commerce Database ERD

```mermaid
erDiagram
    %% Core User Management
    User ||--o{ Address : "has many"
    User ||--o| Cart : "has one"
    User ||--o{ Order : "places"
    User ||--o| Wishlist : "has one"
    User ||--o{ Review : "writes"
    User ||--o{ Session : "has many"
    User ||--o{ APIKey : "owns"

    %% Product Catalog
    Category ||--o{ Product : "contains"
    Product ||--o{ ProductVariant : "has variants"
    Product ||--o{ ProductImage : "has images"
    Product ||--o{ Review : "receives"
    Product ||--o{ InventoryTransaction : "tracks"
    
    ProductImage }o--|| Blob : "references"
    
    %% Shopping Cart
    Cart ||--o{ CartItem : "contains"
    CartItem }o--|| Product : "references"
    CartItem }o--o| ProductVariant : "references"
    Session }o--o| Cart : "LINKS to"

    %% Wishlist
    Wishlist ||--o{ WishlistItem : "contains"
    WishlistItem }o--|| Product : "references"

    %% Orders & Fulfillment
    Order ||--o{ OrderItem : "contains"
    Order ||--o| Payment : "has payment"
    Order ||--o{ Shipment : "has shipments"
    Order ||--o{ Refund : "may have"
    Order ||--o{ Return : "may have"
    
    OrderItem }o--o| Product : "references"
    OrderItem }o--o| ProductVariant : "references"
    OrderItem ||--o{ ShipmentItem : "tracked in"
    
    Shipment ||--o{ ShipmentItem : "contains"
    Shipment }o--o| Blob : "has label"
    
    Payment }o--|| Order : "belongs to"
    Refund }o--|| Order : "belongs to"
    Refund }o--o| Payment : "references"
    Return }o--|| Order : "belongs to"

    %% Background Jobs & Feeds
    Job ||--o| ProductFeed : "processes"
    ProductFeed }o--o| Blob : "references file"
    ProductFeed }o--o| User : "created by"

    %% File Storage
    Blob

    %% Audit & Security
    AuditLog
    APIKey }o--|| User : "belongs to"
    Session }o--o| User : "belongs to"

    %% Promotions
    Coupon

    %% Entity Definitions
    User {
        int id PK
        string email UK
        string first_name
        string last_name
        string hashed_password
        enum role
        bool is_active
        datetime created_at
        datetime updated_at
    }

    Address {
        int id PK
        int user_id FK
        string address_line1
        string address_line2
        string city
        string state
        string country
        string postal_code
        int is_default
    }

    Category {
        int id PK
        string name UK
        text description
        string slug UK
        datetime created_at
        datetime updated_at
    }

    Product {
        int id PK
        string name
        text description
        string slug UK
        int price_cents
        int compare_at_price_cents
        int cost_cents
        string sku UK
        int stock_quantity
        int category_id FK
        bool is_active
        int weight
        string dimensions
        datetime created_at
        datetime updated_at
    }

    ProductVariant {
        int id PK
        int product_id FK
        string sku UK
        string name
        int price_cents
        int compare_at_price_cents
        int cost_cents
        int stock_quantity
        string inventory_management
        string inventory_policy
        bool track_stock
        string option1_name
        string option1_value
        string option2_name
        string option2_value
        string option3_name
        string option3_value
    }

    ProductImage {
        int id PK
        int product_id FK
        int blob_id FK
        string alt_text
        bool is_primary
        int sort_order
    }

    InventoryTransaction {
        int id PK
        int product_id FK
        enum transaction_type
        int quantity_change
        int quantity_after
        string reference_id
        text notes
        datetime created_at
    }

    Cart {
        int id PK
        int user_id FK UK
        datetime created_at
        datetime updated_at
    }

    CartItem {
        int id PK
        int cart_id FK
        int product_id FK
        int variant_id FK
        int quantity
        int unit_price_cents
        json metadata
        datetime added_at
    }

    Wishlist {
        int id PK
        int user_id FK UK
        datetime created_at
        datetime updated_at
    }

    WishlistItem {
        int id PK
        int wishlist_id FK
        int product_id FK
        datetime added_at
    }

    Order {
        int id PK
        int user_id FK
        string order_number UK
        enum status
        int subtotal_cents
        int tax_cents
        int shipping_cost_cents
        int discount_cents
        int total_cents
        string shipping_address_line1
        string shipping_address_line2
        string shipping_city
        string shipping_state
        string shipping_country
        string shipping_postal_code
        text customer_notes
        text admin_notes
        datetime created_at
        datetime updated_at
    }

    OrderItem {
        int id PK
        int order_id FK
        int product_id FK
        int variant_id FK
        string product_name
        string product_sku
        string variant_name
        int quantity
        int unit_price_cents
        int total_price_cents
        int discount_cents
        int tax_cents
    }

    Payment {
        int id PK
        int order_id FK UK
        int amount_cents
        enum method
        enum status
        string transaction_id UK
        text raw_response
        datetime created_at
        datetime updated_at
    }

    Shipment {
        int id PK
        int order_id FK
        string tracking_number UK
        string carrier
        enum status
        int label_blob_id FK
        int cost_cents
        datetime shipped_at
        datetime estimated_delivery
        datetime delivered_at
        text notes
        datetime created_at
        datetime updated_at
    }

    ShipmentItem {
        int id PK
        int shipment_id FK
        int order_item_id FK
        int quantity
    }

    Refund {
        int id PK
        int order_id FK
        int payment_id FK
        int amount_cents
        text reason
        enum status
        text admin_notes
        datetime requested_at
        datetime processed_at
    }

    Return {
        int id PK
        int order_id FK
        text reason
        enum status
        text admin_notes
        datetime requested_at
        datetime approved_at
        datetime received_at
    }

    Review {
        int id PK
        int product_id FK
        int user_id FK
        float rating
        string title
        text comment
        int is_verified_purchase
        datetime created_at
        datetime updated_at
    }

    Coupon {
        int id PK
        string code UK
        text description
        string discount_type
        int discount_value_cents
        int min_purchase_amount_cents
        int max_discount_amount_cents
        json applicable_product_ids
        json applicable_category_ids
        int usage_limit
        int usage_count
        int per_user_limit
        bool is_active
        datetime starts_at
        datetime expires_at
        datetime created_at
        datetime updated_at
    }

    Session {
        int id PK
        string session_token UK
        int cart_id FK
        int user_id FK
        datetime expires_at
        datetime created_at
        datetime last_activity_at
    }

    APIKey {
        int id PK
        int user_id FK
        string key_hash UK
        string name
        json scopes
        bool is_active
        bool is_revoked
        datetime created_at
        datetime expires_at
        datetime last_used_at
    }

    Blob {
        int id PK
        string storage_key UK
        string filename
        string content_type
        bigint size_bytes
        string checksum
        string storage_provider
        datetime created_at
    }

    AuditLog {
        int id PK
        int actor_id
        string actor_type
        string actor_email
        string action
        string target_type
        string target_id
        json metadata
        string ip_address
        text user_agent
        datetime created_at
    }

    Job {
        int id PK
        string job_type
        string idempotency_key UK
        json payload
        json result
        enum status
        string worker_id
        int attempts
        int max_attempts
        json error
        datetime created_at
        datetime started_at
        datetime completed_at
        datetime failed_at
        datetime retry_at
    }

    ProductFeed {
        int id PK
        int blob_id FK
        string filename
        string feed_type
        string format
        enum status
        int total_rows
        int processed_rows
        int success_rows
        int error_rows
        json errors
        int job_id FK
        int created_by_user_id FK
        datetime created_at
        datetime started_at
        datetime completed_at
    }
```

## Key Relationships Summary

### User-Centric (1-to-Many)
- User → Addresses, Orders, Reviews, Sessions, APIKeys
- User → Cart (1-to-1)
- User → Wishlist (1-to-1)

### Product Catalog
- Category → Products (1-to-Many)
- Product → ProductVariants, ProductImages, Reviews (1-to-Many)
- Product → InventoryTransactions (1-to-Many)
- ProductImage → Blob (Many-to-1)

### Shopping Flow
- Cart → CartItems (1-to-Many)
- CartItem → Product, ProductVariant (Many-to-1)
- Session → Cart (Many-to-1, for guest carts)

### Order Fulfillment
- Order → OrderItems, Shipments, Refunds, Returns (1-to-Many)
- Order → Payment (1-to-1)
- OrderItem → Product, ProductVariant (Many-to-1)
- Shipment → ShipmentItems (1-to-Many)
- Shipment → Blob (for shipping label)

### Background Processing
- Job → ProductFeed (1-to-1)
- ProductFeed → Blob, User (Many-to-1)

### Money Fields (Integer Cents)
All monetary values use integer cents to avoid floating-point errors:
- `price_cents`, `amount_cents`, `total_cents`, `cost_cents`, etc.

### JSON Columns
Flexible data stored as JSON:
- `CartItem.metadata` - Product customizations
- `Coupon.applicable_product_ids/applicable_category_ids` - Applicability rules
- `APIKey.scopes` - Permission array
- `AuditLog.metadata` - Event details
- `Job.payload/result/error` - Job data
- `ProductFeed.errors` - Row-level errors
