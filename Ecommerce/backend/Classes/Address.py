class Address:
    def __init__(self, id, recipient_name, company, line1, line2, city, region, postal_code, country, phone, is_validated, validation_errors, created_at, updated_at):
        self.id = id
        self.recipient_name = recipient_name
        self.company = company
        self.line1 = line1
        self.line2 = line2
        self.city = city
        self.region = region
        self.postal_code = postal_code
        self.country = country
        self.phone = phone
        self.is_validated = is_validated
        self.validation_errors = validation_errors
        self.created_at = created_at
        self.updated_at = updated_at