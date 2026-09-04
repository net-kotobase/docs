import re

cold_th = 0.5

lines = open('kz3_run93_out.txt').read().splitlines()
runs = {}
cur = None
for ln in lines:
    m = re.match(r'=== (run\S+|landing control)', ln)
    if m:
        cur = m.group(1)
        runs[cur] = []
    else:
        parts = ln.split()
        if len(parts) == 2:
            runs[cur].append((int(parts[0]), float(parts[1])))

for k, v in runs.items():
    times = sorted(t for c, t in v)
    n = len(v)
    codes = set(c for c, _ in v)
    p50 = times[(n + 1) // 2 - 1]  # nearest-rank, ceil(n*0.5)th
    colds = [t for t in times if t > cold_th]
    print(k, 'n=%d' % n, 'codes=%s' % codes, 'p50=%.3f' % p50,
          'min=%.3f max=%.3f' % (times[0], times[-1]),
          'cold=%d/%d' % (len(colds), n), ['%.3f' % t for t in colds])
