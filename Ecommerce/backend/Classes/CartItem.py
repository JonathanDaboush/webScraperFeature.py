class CartItem:
    def __init__(self, id, cart_id, variant_id, quantity, unit_price_cents, currency, metadata, line_price_cents, created_at, updated_at):
        self.id = id
        self.cart_id = cart_id
        self.variant_id = variant_id
        self.quantity = quantity
        self.unit_price_cents = unit_price_cents
        self.currency = currency
        self.metadata = metadata
        self.line_price_cents = line_price_cents
        self.created_at = created_at
        self.updated_at = updated_at