import time

class RateLimit:
    _MAX_ACTIVE_REQUESTS_KEY = "app:rate_limit:{}:max_active_requests"
    _instance_dict: dict[str, "RateLimit"] = {}

    def __new__(
            cls,
            client_id: str,
            max_active_requests: int,
    ):
        if client_id not in cls._instance_dict:
            instance = super().__new__(cls)
            cls._instance_dict[client_id] = instance
        return cls._instance_dict[client_id]

    def __init__(self, client_id: str, max_active_requests: int):
        self.max_active_requests = max_active_requests
        # must be called after max_active_requests is set
        if self.disabled():
            return
        if hasattr(self, "initialized"):
            return
        self.initialized = True
        self.client_id = client_id

    def flush_cache(
            self,
            use_local_value=False,
    ):
        if self.disabled():
            return

        self.last_recalculate_time = time.time()

    def disabled(self):
        return self.max_active_requests <= 0