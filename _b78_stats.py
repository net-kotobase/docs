import re
txt = open('/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/_b78_run201_out.txt').read()
print(txt[-200:])
sections = re.split(r'=== (.+?) ===\n', txt)[1:]
for i in range(0, len(sections), 2):
    name, body = sections[i], sections[i+1]
    vals = sorted(float(m) for m in re.findall(r'200 ([\d.]+)', body))
    n = len(vals)
    p50 = vals[9]
    p95 = vals[18]
    cold = [v for v in vals if v >= 0.507]
    colds = ', '.join(f'{v:.3f}s@{vals.index(v)+1}' for v in cold) if cold else 'none'
    print(f"{name}: n={n} p50={p50*1000:.0f}ms p95={p95*1000:.0f}ms max={max(vals)*1000:.0f}ms cold(>=0.507s)={len(cold)} [{colds}]")
