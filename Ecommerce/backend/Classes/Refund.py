class Refund:
    def __init__(self, id, order_id, payment_id, amount_cents, reason, status, admin_notes, requested_at, processed_at):
        self.id = id
        self.order_id = order_id
        self.payment_id = payment_id
        self.amount_cents = amount_cents
        self.reason = reason
        self.status = status
        self.admin_notes = admin_notes
        self.requested_at = requested_at
        self.processed_at = processed_at
