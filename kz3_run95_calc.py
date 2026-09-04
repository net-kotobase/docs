#!/usr/bin/env python3
"""Summarize kz3_run95_out.txt: per run n, http codes, cold count (TTFB>=0.5s),
warm p50 (nearest-rank), min/max, cold positions."""
import re
import statistics

path = "/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/kz3_run95_out.txt"
sections = {}
cur = None
with open(path) as f:
    for line in f:
        m = re.match(r"=== (.+) ===", line)
        if m:
            cur = m.group(1)
            sections[cur] = []
        elif cur is not None:
            parts = line.split()
            if len(parts) == 2:
                sections[cur].append((parts[0], float(parts[1])))

def nearest_rank(sorted_vals, p):
    import math
    idx = max(1, math.ceil(p * len(sorted_vals)))
    return sorted_vals[idx - 1]

for name, samples in sections.items():
    codes = [c for c, _ in samples]
    ttfbs = [t for _, t in samples]
    cold = [(i + 1, t) for i, t in enumerate(ttfbs) if t >= 0.5]
    warm = sorted(t for _, t in samples if t < 0.5)
    ok = codes.count("200")
    p50 = nearest_rank(warm, 0.50) if warm else None
    print(f"{name}: n={len(samples)} 200={ok} cold={len(cold)}/20 "
          f"(positions={[p for p, _ in cold]}, TTFB={[round(t,3) for _, t in cold]}) "
          f"warm_p50={p50:.3f}s warm_min={min(warm):.3f}s max={max(ttfbs):.3f}s")
