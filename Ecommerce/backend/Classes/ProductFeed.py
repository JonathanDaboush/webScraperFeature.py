class ProductFeed:
    def __init__(self, id, blob_id, filename, feed_type, format, status, total_rows, processed_rows, success_rows, error_rows, errors, job_id, created_by_user_id, created_at, started_at, completed_at):
        self.id = id
        self.blob_id = blob_id
        self.filename = filename
        self.feed_type = feed_type
        self.format = format
        self.status = status
        self.total_rows = total_rows
        self.processed_rows = processed_rows
        self.success_rows = success_rows
        self.error_rows = error_rows
        self.errors = errors
        self.job_id = job_id
        self.created_by_user_id = created_by_user_id
        self.created_at = created_at
        self.started_at = started_at
        self.completed_at = completed_at
