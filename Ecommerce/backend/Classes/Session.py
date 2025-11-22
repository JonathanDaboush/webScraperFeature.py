class Session:
    def __init__(self, id, session_token, cart_id, user_id, expires_at, created_at, last_activity_at):
        self.id = id
        self.session_token = session_token
        self.cart_id = cart_id
        self.user_id = user_id
        self.expires_at = expires_at
        self.created_at = created_at
        self.last_activity_at = last_activity_at
