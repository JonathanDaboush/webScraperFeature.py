class Review:
    def __init__(self, id, product_id, user_id, rating, title, comment, is_verified_purchase, created_at, updated_at):
        self.id = id
        self.product_id = product_id
        self.user_id = user_id
        self.rating = rating
        self.title = title
        self.comment = comment
        self.is_verified_purchase = is_verified_purchase
        self.created_at = created_at
        self.updated_at = updated_at
