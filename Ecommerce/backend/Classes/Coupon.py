class Coupon:
    def __init__(self, id, code, description, discount_type, discount_value_cents, min_purchase_amount_cents, max_discount_amount_cents, applicable_product_ids, applicable_category_ids, usage_limit, usage_count, per_user_limit, is_active, starts_at, expires_at, created_at, updated_at):
        self.id = id
        self.code = code
        self.description = description
        self.discount_type = discount_type
        self.discount_value_cents = discount_value_cents
        self.min_purchase_amount_cents = min_purchase_amount_cents
        self.max_discount_amount_cents = max_discount_amount_cents
        self.applicable_product_ids = applicable_product_ids
        self.applicable_category_ids = applicable_category_ids
        self.usage_limit = usage_limit
        self.usage_count = usage_count
        self.per_user_limit = per_user_limit
        self.is_active = is_active
        self.starts_at = starts_at
        self.expires_at = expires_at
        self.created_at = created_at
        self.updated_at = updated_at