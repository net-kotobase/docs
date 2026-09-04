#!/usr/bin/env python3
import re, statistics

lines = open('/tmp/kz3_run79_out.txt').read().splitlines()
runs = {}
cur = None
for ln in lines:
    m = re.match(r'=== run(\S+) search ===', ln)
    if m:
        cur = m.group(1); runs[cur] = []
        continue
    if ln.startswith('=== landing control ==='):
        cur = 'CTRL'; runs[cur] = []
        continue
    m = re.match(r'(\d+) ([\d.]+)', ln)
    if m and cur:
        runs[cur].append((int(m.group(1)), float(m.group(2))))

for rid, vals in runs.items():
    codes = [c for c, _ in vals]
    t = sorted(t for _, t in vals)
    n = len(t)
    p50 = t[n // 2] if n % 2 == 1 else (t[n // 2 - 1] + t[n // 2]) / 2
    cold = [x for x in t if x >= 0.5]
    warm = [x for x in t if x < 0.5]
    wp50 = sorted(warm)[len(warm) // 2] if warm else None
    print(f"run{rid}: n={n} all200={all(c == 200 for c in codes)} "
          f"cold={len(cold)}/{n} cold_range=({min(cold):.3f}-{max(cold):.3f})" if cold else
          f"run{rid}: n={n} all200={all(c == 200 for c in codes)} cold=0/{n}", end='')
    print(f" p50={p50:.3f} min={t[0]:.3f} max={t[-1]:.3f} warm_p50={wp50:.3f}" if wp50 else "")
    # cold positions (1-indexed)
    pos = [i + 1 for i, (c, x) in enumerate(vals) if x >= 0.5]
    if pos:
        print(f"  cold positions: {pos}")
