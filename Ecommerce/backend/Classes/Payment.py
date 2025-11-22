class Payment:
    def __init__(self, id, order_id, amount_cents, method, status, transaction_id, raw_response, created_at, updated_at):
        self.id = id
        self.order_id = order_id
        self.amount_cents = amount_cents
        self.method = method
        self.status = status
        self.transaction_id = transaction_id
        self.raw_response = raw_response
        self.created_at = created_at
        self.updated_at = updated_at