import re
lines = open('kz3_run122_out.txt').read().splitlines()
rid = None
stats = {}
for l in lines:
    m = re.match(r'=== run(\S+) search ===', l)
    if m: rid = m.group(1); stats[rid] = []
    elif 'landing control' in l: rid = 'CTRL'; stats[rid] = []
    else:
        m = re.match(r'(\d+) (\S+)', l)
        if m and rid: stats[rid].append((int(m.group(1)), float(m.group(2))))
for k, v in stats.items():
    t = sorted(x[1] for x in v)
    codes = {}
    for c, _ in v: codes[c] = codes.get(c, 0) + 1
    cold = sum(1 for x in t if x >= 0.5)
    n = len(t)
    print(k, 'n=%d' % n, 'codes=%s' % codes,
          'p50=%.3f' % t[n//2], 'p90=%.3f' % t[int(n*0.9)-1], 'max=%.3f' % t[-1],
          'cold(>=0.5s)=%d/%d' % (cold, n))
