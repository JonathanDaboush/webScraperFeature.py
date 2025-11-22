class InventoryTransaction:
    def __init__(self, id, product_id, transaction_type, quantity_change, quantity_after, reference_id, notes, created_at):
        self.id = id
        self.product_id = product_id
        self.transaction_type = transaction_type
        self.quantity_change = quantity_change
        self.quantity_after = quantity_after
        self.reference_id = reference_id
        self.notes = notes
        self.created_at = created_at