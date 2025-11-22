class ShipmentItem:
    def __init__(self, id, shipment_id, order_item_id, quantity):
        self.id = id
        self.shipment_id = shipment_id
        self.order_item_id = order_item_id
        self.quantity = quantity
