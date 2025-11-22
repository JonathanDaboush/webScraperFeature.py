class Address:
    def __init__(self, id, user_id, address_line1, address_line2, city, state, country, postal_code, is_default):
        self.id = id
        self.user_id = user_id
        self.address_line1 = address_line1
        self.address_line2 = address_line2
        self.city = city
        self.state = state
        self.country = country
        self.postal_code = postal_code
        self.is_default = is_default