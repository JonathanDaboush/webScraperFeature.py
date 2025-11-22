class Blob:
    def __init__(self, id, storage_key, filename, content_type, size_bytes, checksum, storage_provider, created_at):
        self.id = id
        self.storage_key = storage_key
        self.filename = filename
        self.content_type = content_type
        self.size_bytes = size_bytes
        self.checksum = checksum
        self.storage_provider = storage_provider
        self.created_at = created_at
