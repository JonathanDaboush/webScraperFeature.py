class Job:
    def __init__(
        self,
        id,
        type,
        payload,
        status,                     # queued / running / completed / failed
        idempotency_key,
        result,
        error,
        attempts,
        created_at,
        updated_at,
        started_at=None,
        completed_at=None,
        worker_id=None
    ):
        self.id = id
        self.type = type
        self.payload = payload
        self.status = status
        self.idempotency_key = idempotency_key
        self.result = result
        self.error = error
        self.attempts = attempts
        self.created_at = created_at
        self.updated_at = updated_at
        self.started_at = started_at
        self.completed_at = completed_at
        self.worker_id = worker_id

    def enqueue(self):
        pass

    def start(self, worker_id):
        pass

    def complete(self, result):
        pass

    def fail(self, error, retry=False):
        pass
