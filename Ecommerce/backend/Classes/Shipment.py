class Shipment:
    def __init__(self, id, order_id, tracking_number, carrier, status, label_blob_id, cost_cents, shipped_at, estimated_delivery, delivered_at, notes, created_at, updated_at):
        self.id = id
        self.order_id = order_id
        self.tracking_number = tracking_number
        self.carrier = carrier
        self.status = status
        self.label_blob_id = label_blob_id
        self.cost_cents = cost_cents
        self.shipped_at = shipped_at
        self.estimated_delivery = estimated_delivery
        self.delivered_at = delivered_at
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at