class Blob:
    def __init__(
        self,
        id,
        storage_key,
        filename,
        mimetype,
        size_bytes,
        checksum,
        metadata,
        created_at,
        updated_at
    ):
        self.id = id
        self.storage_key = storage_key
        self.filename = filename
        self.mimetype = mimetype
        self.size_bytes = size_bytes
        self.checksum = checksum
        self.metadata = metadata or {}
        self.created_at = created_at
        self.updated_at = updated_at

    def get_signed_url(self, ttl_seconds):
        pass

    def open_stream(self):
        pass
