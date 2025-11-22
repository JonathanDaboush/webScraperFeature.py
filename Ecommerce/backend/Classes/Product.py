class Product:
    def __init__(self, id, name, description, slug, price_cents, compare_at_price_cents, cost_cents, sku, stock_quantity, category_id, is_active, weight, dimensions, created_at, updated_at):
        self.id = id
        self.name = name
        self.description = description
        self.slug = slug
        self.price_cents = price_cents
        self.compare_at_price_cents = compare_at_price_cents
        self.cost_cents = cost_cents
        self.sku = sku
        self.stock_quantity = stock_quantity
        self.category_id = category_id
        self.is_active = is_active
        self.weight = weight
        self.dimensions = dimensions
        self.created_at = created_at
        self.updated_at = updated_at