class Payment:
    def __init__(self, id, order_id, gateway, amount_cents, currency, status, transaction_id, raw_response, captured_at, created_at, updated_at):
        self.id = id
        self.order_id = order_id
        self.gateway = gateway
        self.amount_cents = amount_cents
        self.currency = currency
        self.status = status
        self.transaction_id = transaction_id
        self.raw_response = raw_response
        self.captured_at = captured_at
        self.created_at = created_at
        self.updated_at = updated_at