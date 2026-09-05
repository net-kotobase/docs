import re, statistics, sys
lines = open("kz3_run155_out.txt").read().splitlines()
sections = {}
cur = None
for ln in lines:
    m = re.match(r"=== run(\w+) search", ln)
    if m:
        cur = "run" + m.group(1); sections[cur] = []; continue
    if ln.startswith("=== landing"):
        cur = "control"; sections[cur] = []; continue
    m = re.match(r"(\d{3}) ([\d.]+)", ln)
    if m and cur:
        sections[cur].append((int(m.group(1)), float(m.group(2))))
summary = []
for name, vals in sections.items():
    codes = [c for c, t in vals]
    ts = sorted(t for c, t in vals if c == 200)
    cold = [t for t in ts if t >= 0.5]
    n = len(ts)
    if ts:
        def pct(p):
            import math
            k = max(1, math.ceil(p * n))
            return ts[k - 1]
        summary.append((name, n, codes.count(200), len(cold),
                        min(ts), pct(0.5), pct(0.9), max(ts),
                        [round(t, 3) for t in cold]))
out = "\n".join(
    f"{name}: n200={ok}/{n} cold>=0.5s={len(cold)} p50={p50*1000:.1f}ms p90={p90*1000:.1f}ms max={mx*1000:.1f}ms colds={colds}"
    for name, n, ok, cnt, mn, p50, p90, mx, colds in summary)
print(out)
open("kz3_run155_calc.txt", "w").write(out + "\n")
