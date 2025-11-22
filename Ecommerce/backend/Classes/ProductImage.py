class ProductImage:
    def __init__(self, id, product_id, blob_id, alt_text, is_primary, sort_order):
        self.id = id
        self.product_id = product_id
        self.blob_id = blob_id
        self.alt_text = alt_text
        self.is_primary = is_primary
        self.sort_order = sort_order