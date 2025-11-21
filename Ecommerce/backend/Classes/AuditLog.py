class AuditLog:
    def __init__(
        self,
        id,
        actor_id,
        action,
        target_type,
        target_id,
        metadata,
        created_at
    ):
        self.id = id
        self.actor_id = actor_id
        self.action = action
        self.target_type = target_type
        self.target_id = target_id
        self.metadata = metadata or {}
        self.created_at = created_at

    def to_dict(self):
        pass
