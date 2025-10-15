# aggregate_reports.py
import glob
import pandas as pd
import os

def aggregate():
    files = sorted(glob.glob("reports/test_results_*.csv"))
    rows = []
    for f in files:
        df = pd.read_csv(f)
        total = len(df)
        passed = (df['status']=="PASS").sum()
        failed = total - passed
        ts = os.path.basename(f).replace("test_results_", "").replace(".csv", "")
        rows.append({"file": f, "ts": ts, "total": total, "passed": int(passed), "failed": int(failed)})
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = aggregate()
    print(df.to_markdown(index=False))