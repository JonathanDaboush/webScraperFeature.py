class APIKey:
    def __init__(self, id, user_id, key_hash, name, scopes, is_active, is_revoked, created_at, expires_at, last_used_at):
        self.id = id
        self.user_id = user_id
        self.key_hash = key_hash
        self.name = name
        self.scopes = scopes
        self.is_active = is_active
        self.is_revoked = is_revoked
        self.created_at = created_at
        self.expires_at = expires_at
        self.last_used_at = last_used_at
