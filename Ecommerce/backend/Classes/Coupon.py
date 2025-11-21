class Coupon:
    def __init__(self, id, code, coupon_type, value_cents, value_percent, free_shipping, starts_at, expires_at, usage_limit, uses_count, per_user_limit, applicable_product_ids, applicable_category_ids, min_order_cents, is_active, created_at, updated_at, metadata):
        self.id = id
        self.code = code
        self.coupon_type = coupon_type  # 'percent'|'fixed'|'free_shipping' etc.
        self.value_cents = value_cents
        self.value_percent = value_percent
        self.free_shipping = free_shipping
        self.starts_at = starts_at
        self.expires_at = expires_at
        self.usage_limit = usage_limit
        self.uses_count = uses_count
        self.per_user_limit = per_user_limit
        self.applicable_product_ids = applicable_product_ids
        self.applicable_category_ids = applicable_category_ids
        self.min_order_cents = min_order_cents
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
        self.metadata = metadata