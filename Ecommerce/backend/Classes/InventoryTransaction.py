class InventoryTransaction:
    def __init__(self, id, variant_id, delta, type, reference_id, actor_id, note, timestamp, created_at):
        self.id = id
        self.variant_id = variant_id
        self.delta = delta
        self.type = type
        self.reference_id = reference_id
        self.actor_id = actor_id
        self.note = note
        self.timestamp = timestamp
        self.created_at = created_at