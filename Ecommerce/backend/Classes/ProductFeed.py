class ProductFeed:
    def __init__(
        self,
        id,
        file_blob_id,
        status,
        row_errors,        # list of structured row error objects
        job_id,
        created_at,
        updated_at
    ):
        self.id = id
        self.file_blob_id = file_blob_id
        self.status = status
        self.row_errors = row_errors or []
        self.job_id = job_id
        self.created_at = created_at
        self.updated_at = updated_at

    def start(self):
        pass
