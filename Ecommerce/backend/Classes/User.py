class User:
    def __init__(self, id, email, first_name, last_name, hashed_password, role, is_active, created_at, updated_at):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.hashed_password = hashed_password
        self.role = role
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
