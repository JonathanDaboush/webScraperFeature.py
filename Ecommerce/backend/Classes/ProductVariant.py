class ProductVariant:
    def __init__(self, id, product_id, sku, name, price_cents, compare_at_price_cents, cost_cents, stock_quantity, inventory_management, inventory_policy, track_stock, option1_name, option1_value, option2_name, option2_value, option3_name, option3_value):
        self.id = id
        self.product_id = product_id
        self.sku = sku
        self.name = name
        self.price_cents = price_cents
        self.compare_at_price_cents = compare_at_price_cents
        self.cost_cents = cost_cents
        self.stock_quantity = stock_quantity
        self.inventory_management = inventory_management
        self.inventory_policy = inventory_policy
        self.track_stock = track_stock
        self.option1_name = option1_name
        self.option1_value = option1_value
        self.option2_name = option2_name
        self.option2_value = option2_value
        self.option3_name = option3_name
        self.option3_value = option3_value