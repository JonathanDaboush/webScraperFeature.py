class AuditLog:
    def __init__(self, id, actor_id, actor_type, actor_email, action, target_type, target_id, metadata, ip_address, user_agent, created_at):
        self.id = id
        self.actor_id = actor_id
        self.actor_type = actor_type
        self.actor_email = actor_email
        self.action = action
        self.target_type = target_type
        self.target_id = target_id
        self.metadata = metadata
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.created_at = created_at
