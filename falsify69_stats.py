import sys
f = sys.argv[1]
vals = []
cold = 0
codes = {}
samples = []
for l in open(f):
    p = l.split()
    if len(p) >= 4 and p[0] in ("178A","178B","178C","LC"):
        run, i, ttfb, code = p[0], p[1], float(p[2]), p[3]
        codes[code] = codes.get(code, 0) + 1
        if run != "LC":
            vals.append(ttfb)
            if ttfb >= 0.5:
                cold += 1
                samples.append((run, i, ttfb))
        else:
            if ttfb >= 0.5:
                samples.append(("LC", i, ttfb))
vals.sort()
import statistics
n = len(vals)
def q(pct):
    idx = max(0, min(n-1, int((n-1)*pct/100)))
    return vals[idx]
print(f"search n={n} cold(>=0.5s)={cold} p50={q(50)*1000:.1f}ms p95={q(95)*1000:.1f}ms min={vals[0]*1000:.1f}ms max={vals[-1]*1000:.1f}ms")
print(f"codes={codes}")
print(f"cold list: {samples}")
per = {}
for l in open(f):
    p = l.split()
    if len(p) >= 4 and p[0] in ("178A","178B","178C"):
        ttfb = float(p[2])
        d = per.setdefault(p[0], [0,0.0,[]])
        d[0] += 1
        if ttfb >= 0.5: d[1] += 1
        d[2].append(ttfb)
for k in sorted(per):
    c, coldc, arr = per[k]
    arr.sort()
    print(f"{k}: cold={int(coldc)}/{c} p50={arr[len(arr)//2]*1000:.1f}ms max={arr[-1]*1000:.1f}ms")
