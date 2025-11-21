class ProductImage:
    def __init__(self, id, blob_id, product_id, variant_override_id, alt_text, position, width, height, content_type, is_primary, created_at, updated_at):
        self.id = id
        self.blob_id = blob_id
        self.product_id = product_id
        self.variant_override_id = variant_override_id
        self.alt_text = alt_text
        self.position = position
        self.width = width
        self.height = height
        self.content_type = content_type
        self.is_primary = is_primary
        self.created_at = created_at
        self.updated_at = updated_at