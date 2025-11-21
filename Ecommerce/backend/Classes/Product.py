class Product:
    def __init__(self, id, title, description, short_description, slug, category_ids, image_ids, default_variant_id, status, tags, seo_meta, created_at, updated_at):
        self.id = id
        self.title = title
        self.description = description
        self.short_description = short_description
        self.slug = slug
        self.category_ids = category_ids
        self.image_ids = image_ids
        self.default_variant_id = default_variant_id
        self.status = status
        self.tags = tags
        self.seo_meta = seo_meta
        self.created_at = created_at
        self.updated_at = updated_at