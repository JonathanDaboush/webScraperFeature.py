class APIKey:
    def __init__(
        self,
        id,
        name,
        hashed_key,
        scopes,               # list[str]
        revoked,
        expires_at,
        created_by,
        created_at,
        updated_at
    ):
        self.id = id
        self.name = name
        self.hashed_key = hashed_key
        self.scopes = scopes
        self.revoked = revoked
        self.expires_at = expires_at
        self.created_by = created_by
        self.created_at = created_at
        self.updated_at = updated_at

    def check_scope(self, scope):
        pass

    def revoke(self, actor_id):
        pass
