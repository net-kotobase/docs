import re
lines = [l.split() for l in open('_b71_meas.txt') if l.strip()]
groups = {}
for l in lines:
    if l[0] == 'DONE':
        print(' '.join(l)); continue
    t, code = float(l[2]), l[3]
    groups.setdefault(l[0], []).append((t, code))
for g, vals in groups.items():
    n = len(vals)
    codes_ok = sum(1 for _, c in vals if c == '200')
    times = sorted(t for t, _ in vals)
    # nearest-rank p50: ceil(0.5*n)-th (1-indexed)
    p50 = times[(n + 1) // 2 - 1]
    cold = sum(1 for t in times if t >= 0.5)
    print(f"{g}: n={n} 200={codes_ok} cold(>=0.5s)={cold}/{n} p50={p50*1000:.0f}ms max={times[-1]*1000:.0f}ms")
