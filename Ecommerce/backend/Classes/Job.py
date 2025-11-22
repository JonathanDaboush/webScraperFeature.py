class Job:
    def __init__(self, id, job_type, idempotency_key, payload, result, status, worker_id, attempts, max_attempts, error, created_at, started_at, completed_at, failed_at, retry_at):
        self.id = id
        self.job_type = job_type
        self.idempotency_key = idempotency_key
        self.payload = payload
        self.result = result
        self.status = status
        self.worker_id = worker_id
        self.attempts = attempts
        self.max_attempts = max_attempts
        self.error = error
        self.created_at = created_at
        self.started_at = started_at
        self.completed_at = completed_at
        self.failed_at = failed_at
        self.retry_at = retry_at
