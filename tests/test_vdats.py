import random
import datetime

import pytest

from dut import VirtualSensor
from test_automation import run_tests


def test_readings_within_range_and_not_none_when_fail_rate_zero():
    # deterministic RNG injected
    rng = random.Random(0)
    s = VirtualSensor(min_temp=10.0, max_temp=20.0, fail_rate=0.0, rng=rng)
    for _ in range(20):
        r = s.read_temperature()
        assert r is not None
        assert 10.0 <= r <= 20.0


def test_all_none_when_fail_rate_one():
    rng = random.Random(1)
    s = VirtualSensor(fail_rate=1.0, rng=rng)
    for _ in range(10):
        assert s.read_temperature() is None


def test_run_tests_structure_and_timestamps():
    results = run_tests(iterations=5)
    assert len(results) == 5
    for idx, row in enumerate(results, start=1):
        assert row['test_id'] == idx
        assert 'reading' in row
        assert 'status' in row
        assert 'timestamp_utc' in row
        # ensure timestamp parses as ISO 8601 (with trailing Z)
        ts = row['timestamp_utc']
        # fromisoformat expects +00:00 instead of Z
        datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))