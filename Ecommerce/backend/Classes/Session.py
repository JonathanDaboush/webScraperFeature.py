class Session:
    def __init__(
        self,
        id,
        token,
        cart_id,
        expires_at,
        metadata,
        created_at,
        updated_at
    ):
        self.id = id
        self.token = token
        self.cart_id = cart_id
        self.expires_at = expires_at
        self.metadata = metadata or {}
        self.created_at = created_at
        self.updated_at = updated_at

    def touch(self):
        pass
