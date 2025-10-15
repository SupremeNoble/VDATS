# dut.py
import random

from datetime import datetime, timezone
from typing import Optional


class VirtualSensor:
    def __init__(self, min_temp: float = 20.0, max_temp: float = 30.0, fail_rate: float = 0.05,
                 rng: Optional[random.Random] = None):
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.fail_rate = fail_rate
        # Use injected RNG for deterministic tests; fall back to a new Random() if not provided
        self._rng = rng or random.Random()

    def read_temperature(self) -> Optional[float]:
        # Simulate transient failures using injected RNG
        if self._rng.random() < self.fail_rate:
            return None
        return round(self._rng.uniform(self.min_temp, self.max_temp), 2)

    def metadata(self):
        return {
            "device_id": "VDS-001",
            "model": "virtual-sensor-1",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }