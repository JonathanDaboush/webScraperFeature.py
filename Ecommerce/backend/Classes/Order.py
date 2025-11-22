class Order:
    def __init__(self, id, user_id, order_number, status, subtotal_cents, tax_cents, shipping_cost_cents, discount_cents, total_cents, shipping_address_line1, shipping_address_line2, shipping_city, shipping_state, shipping_country, shipping_postal_code, customer_notes, admin_notes, created_at, updated_at):
        self.id = id
        self.user_id = user_id
        self.order_number = order_number
        self.status = status
        self.subtotal_cents = subtotal_cents
        self.tax_cents = tax_cents
        self.shipping_cost_cents = shipping_cost_cents
        self.discount_cents = discount_cents
        self.total_cents = total_cents
        self.shipping_address_line1 = shipping_address_line1
        self.shipping_address_line2 = shipping_address_line2
        self.shipping_city = shipping_city
        self.shipping_state = shipping_state
        self.shipping_country = shipping_country
        self.shipping_postal_code = shipping_postal_code
        self.customer_notes = customer_notes
        self.admin_notes = admin_notes
        self.created_at = created_at
        self.updated_at = updated_at