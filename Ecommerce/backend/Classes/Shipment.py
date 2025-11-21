class Shipment:
    def __init__(self, id, order_id, carrier, service, tracking_number, label_url, shipment_items, status, shipped_at, delivered_at, created_at, updated_at):
        self.id = id
        self.order_id = order_id
        self.carrier = carrier
        self.service = service
        self.tracking_number = tracking_number
        self.label_url = label_url
        self.shipment_items = shipment_items  # list of {variant_id, quantity, order_line_id}
        self.status = status
        self.shipped_at = shipped_at
        self.delivered_at = delivered_at
        self.created_at = created_at
        self.updated_at = updated_at