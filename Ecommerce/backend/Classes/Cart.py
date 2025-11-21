class Cart:
    def __init__(self, id, user_id, session_id, currency, items, coupon_codes, subtotal_cents, discounts_cents, tax_cents, shipping_cents, total_cents, created_at, updated_at, expires_at, last_merged_at):
        self.id = id
        self.user_id = user_id
        self.session_id = session_id
        self.currency = currency
        self.items = items  # list[CartItem]
        self.coupon_codes = coupon_codes  # list[str]
        self.subtotal_cents = subtotal_cents
        self.discounts_cents = discounts_cents
        self.tax_cents = tax_cents
        self.shipping_cents = shipping_cents
        self.total_cents = total_cents
        self.created_at = created_at
        self.updated_at = updated_at
        self.expires_at = expires_at
        self.last_merged_at = last_merged_at