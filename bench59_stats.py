import json, math

rows = []
cur = None
for line in open('/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/bench59_run172_out.txt'):
    line = line.strip()
    if line.startswith('=== run172'):
        cur = line.split()[1]
        rows.append((cur, []))
        continue
    if line.startswith('=== landing'):
        cur = 'LC'
        rows.append((cur, []))
        continue
    parts = line.split()
    if len(parts) == 4 and parts[0] in ('172A','172B','172C','LC'):
        t, code = float(parts[2]), parts[3]
        for name, lst in rows:
            if name == cur:
                lst.append((t, code))
out = []
for name, lst in rows:
    ts = [t for t, c in lst]
    codes = sorted(set(c for t, c in lst))
    s = sorted(ts)
    p50 = s[math.ceil(0.50 * len(s)) - 1] if s else None
    cold = [t for t in ts if t >= 0.5]
    out.append({'run': name, 'n': len(ts), 'codes': codes, 'p50_ms': round(p50*1000) if p50 else None,
                'cold_ge_0.5s': len(cold), 'cold_list': [round(t,3) for t in cold]})
print(json.dumps(out, indent=1))
open('/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/bench59_stats.json','w').write(json.dumps(out, indent=1))
