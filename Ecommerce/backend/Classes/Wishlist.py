class Wishlist:
    def __init__(
        self,
        id,
        user_id,
        variant_ids,          # list[UUID]
        created_at,
        updated_at
    ):
        self.id = id
        self.user_id = user_id
        self.variant_ids = variant_ids
        self.created_at = created_at
        self.updated_at = updated_at

    def add(self, variant_id):
        pass

    def remove(self, variant_id):
        pass
