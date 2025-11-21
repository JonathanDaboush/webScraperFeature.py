class Order:
    def __init__(self, id, order_number, user_id, status, currency, items, subtotal_cents, discounts_cents, tax_cents, shipping_cents, total_cents, payment_id, payments, shipments, billing_address_snapshot, shipping_address_snapshot, coupon_codes, metadata, created_at, updated_at):
        self.id = id
        self.order_number = order_number
        self.user_id = user_id
        self.status = status
        self.currency = currency
        self.items = items  # frozen snapshot list (sku, variant_id, title, quantity, unit_price_cents, line_total_cents)
        self.subtotal_cents = subtotal_cents
        self.discounts_cents = discounts_cents
        self.tax_cents = tax_cents
        self.shipping_cents = shipping_cents
        self.total_cents = total_cents
        self.payment_id = payment_id  # primary payment record id
        self.payments = payments  # list[Payment]
        self.shipments = shipments  # list[Shipment]
        self.billing_address_snapshot = billing_address_snapshot  # Address snapshot dict
        self.shipping_address_snapshot = shipping_address_snapshot  # Address snapshot dict
        self.coupon_codes = coupon_codes
        self.metadata = metadata
        self.created_at = created_at
        self.updated_at = updated_at