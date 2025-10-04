"""
Run:
  python eval/rlt_harness.py data/sessions/*.json --tau 0.75 --window 6
"""
import json, argparse, glob
from statistics import mean

def rlt(session, tau=0.75, window=6):
    hist = session.get("history", [])
    vals, passes = [], []
    for i in range(len(hist)):
        w = hist[max(0, i-window+1):i+1]
        avg = mean(h["metrics"]["r"] for h in w if "metrics" in h and "r" in h["metrics"]) if w else 0.0
        vals.append(avg)
        passes.append(avg >= tau)
    return dict(
        session_id=session.get("session_id","unknown"),
        time_above_tau=sum(passes),
        pass_rate=(sum(passes)/max(1,len(passes))) if passes else 0.0,
        series=vals
    )

if __name__ == "__main__":
    import argparse, glob, json
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--tau", type=float, default=0.75)
    ap.add_argument("--window", type=int, default=6)
    args = ap.parse_args()

    for pattern in args.paths:
        for path in glob.glob(pattern):
            with open(path) as f:
                s = json.load(f)
            res = rlt(s, tau=args.tau, window=args.window)
            print(path, "time≥τ:", res["time_above_tau"], "pass_rate:", round(res["pass_rate"], 2))
