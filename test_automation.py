# test_automation.py
import csv
from datetime import datetime, timezone
import os
import argparse
import random
from typing import Optional
from dut import VirtualSensor

OUTDIR = "reports"
os.makedirs(OUTDIR, exist_ok=True)

def run_tests(iterations=100, spec_min=20.0, spec_max=30.0, rng: Optional[random.Random] = None):
    # Inject RNG into VirtualSensor for deterministic runs/tests
    sensor = VirtualSensor(rng=rng)
    results = []
    for i in range(iterations):
        reading = sensor.read_temperature()
        status = "PASS" if (reading is not None and spec_min <= reading <= spec_max) else "FAIL"
        row = {
            "test_id": i+1,
            "reading": reading,
            "status": status,
            "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        results.append(row)
    return results

def save_results(results):
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = os.path.join(OUTDIR, f"test_results_{ts}.csv")
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print("Saved:", filename)
    return filename

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run VDATS simulated tests')
    parser.add_argument('--iterations', '-n', type=int, default=100, help='Number of test iterations')
    parser.add_argument('--seed', type=int, default=None, help='Optional RNG seed for deterministic runs')
    args = parser.parse_args()

    rng = random.Random(args.seed) if args.seed is not None else None
    results = run_tests(iterations=args.iterations, rng=rng)
    save_results(results)