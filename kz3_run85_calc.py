import sys
lines = open(sys.argv[1]).read().splitlines()
block = None
data = {}
for ln in lines:
    ln = ln.strip()
    if ln.startswith("=== run") or ln.startswith("=== landing"):
        block = ln.strip("= ")
        data[block] = []
    elif " " in ln and block:
        code, ttfb = ln.split()
        data[block].append((code, float(ttfb)))
for k, v in data.items():
    codes = [c for c, _ in v]
    ts = sorted(t for _, t in v)
    cold = [t for t in ts if t >= 0.5]
    n = len(ts)
    p50 = ts[(n + 1) // 2 - 1] if n else 0
    p95 = ts[min(n - 1, int((n + 1) * 0.95) - 1)] if n else 0
    ok = sum(1 for c in codes if c == "200")
    print(f"{k}: n={n} 200={ok} cold(>=0.5s)={len(cold)} cold_detail={cold} p50={p50:.3f}s p95={p95:.3f}s min={ts[0]:.3f}s max={ts[-1]:.3f}s")
