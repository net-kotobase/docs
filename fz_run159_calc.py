import re

out = open('/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/fz_run159_out.txt').read().splitlines()
cur = None
data = {}
for line in out:
    m = re.match(r'=== (run159([ABC]) search|landing control)', line)
    if m:
        cur = 'LC' if m.group(1) == 'landing control' else m.group(2)
        data[cur] = []
        continue
    p = line.split()
    if cur and len(p) == 4 and (p[0] == 'LC' or p[0].startswith('159')):
        try:
            data[cur].append((float(p[-2]), p[-1]))
        except ValueError:
            continue

def pct(s, q):
    s = sorted(s)
    idx = max(0, int(len(s)*q) - 1)
    return s[idx]

for k in ['A', 'B', 'C', 'LC']:
    ts = [t for t, c in data[k]]
    codes = set(c for t, c in data[k])
    cold = [t for t in ts if t >= 0.5]
    print(f"{k}: n={len(ts)} codes={codes} cold(>=0.5s)={len(cold)}/{len(ts)} p50={pct(ts,0.5):.3f} p90={pct(ts,0.9):.3f} min={min(ts):.3f} max={max(ts):.3f} coldvals={[f'{t:.3f}' for t in cold]}")
print("timestamp first/last:", out[0], "|", out[-1])
