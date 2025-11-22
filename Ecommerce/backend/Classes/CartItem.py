class CartItem:
    def __init__(self, id, cart_id, product_id, variant_id, quantity, unit_price_cents, metadata, added_at):
        self.id = id
        self.cart_id = cart_id
        self.product_id = product_id
        self.variant_id = variant_id
        self.quantity = quantity
        self.unit_price_cents = unit_price_cents
        self.metadata = metadata
        self.added_at = added_at