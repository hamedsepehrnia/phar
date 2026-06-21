"""Throttling with jitter for crawler requests."""
import random
import time


class CrawlRateLimiter:
    def __init__(
        self,
        min_delay: float = 2.0,
        max_delay: float = 5.0,
        batch_size: int = 15,
        batch_pause: float = 60.0,
    ):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.batch_size = batch_size
        self.batch_pause = batch_pause

    def throttle(self, multiplier: float = 1.0):
        delay = random.uniform(self.min_delay, self.max_delay) * multiplier
        time.sleep(delay)

    def maybe_batch_pause(self, item_index: int):
        if self.batch_size > 0 and item_index > 0 and item_index % self.batch_size == 0:
            time.sleep(self.batch_pause)
