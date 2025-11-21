class Category:
    def __init__(self, id, name, slug, parent_id, is_visible, metadata, position, created_at, updated_at):
        self.id = id
        self.name = name
        self.slug = slug
        self.parent_id = parent_id
        self.is_visible = is_visible
        self.metadata = metadata
        self.position = position
        self.created_at = created_at
        self.updated_at = updated_at