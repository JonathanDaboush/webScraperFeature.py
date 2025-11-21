class ProductVariant:
    def __init__(self, id, product_id, sku, title, price_cents, compare_at_price_cents, currency, track_stock, stock_quantity, inventory_management, inventory_policy, weight, dimensions, is_active, created_at, updated_at):
        self.id = id
        self.product_id = product_id
        self.sku = sku
        self.title = title
        self.price_cents = price_cents
        self.compare_at_price_cents = compare_at_price_cents
        self.currency = currency
        self.track_stock = track_stock
        self.stock_quantity = stock_quantity
        self.inventory_management = inventory_management
        self.inventory_policy = inventory_policy
        self.weight = weight
        self.dimensions = dimensions
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at