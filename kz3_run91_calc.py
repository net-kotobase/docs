import sys, re
lines = open('kz3_run91_out.txt').read().splitlines()
secs, cur = {}, None
for ln in lines:
    m = re.match(r'=== run(\S+) search ===', ln)
    if m: cur = m.group(1); secs[cur] = []
    elif ln.startswith('=== landing'): cur = 'CTRL'; secs[cur] = []
    elif cur and ln.strip():
        code, t = ln.split(); secs[cur].append((code, float(t)))
for name, vals in secs.items():
    ts = sorted(t for c, t in vals if c == '200')
    cold = sum(1 for c, t in vals if c == '200' and t > 0.5)
    p50 = ts[(len(ts)+1)//2 - 1] if ts else float('nan')
    codes = sorted(set(c for c, _ in vals))
    print(f"{name}: n={len(vals)} codes={codes} cold(>0.5s)={cold}/{len(vals)} p50={p50:.3f}s min={min(ts):.3f} max={max(ts):.3f}" if ts else f"{name}: no 200s")
