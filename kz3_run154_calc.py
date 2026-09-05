import re

lines = open('kz3_run154_out.txt').read().splitlines()
runs = {}
cur = None
for l in lines:
    m = re.match(r'=== run(\w+) search ===', l)
    if m:
        cur = 'run' + m.group(1); runs[cur] = []
    elif l == '=== landing control ===':
        cur = 'control'; runs[cur] = []
    else:
        m = re.match(r'(\d+) ([\d.]+)', l)
        if m and cur:
            runs[cur].append((int(m.group(1)), float(m.group(2))))

for k, v in runs.items():
    ts = sorted(t for _, t in v)
    n = len(ts)
    p50 = ts[n // 2]
    cold = sum(1 for _, t in v if t >= 1.0)
    mx = max(ts)
    codes = set(c for c, _ in v)
    print(f"{k}: n={n} codes={codes} cold(>=1s)={cold}/{n} p50={p50*1000:.1f}ms max={mx*1000:.1f}ms")
