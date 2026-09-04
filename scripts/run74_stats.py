import sys

def stats(path):
    vals = sorted(float(x) for x in open(path).read().split())
    n = len(vals)
    cold = [v for v in vals if v > 0.5]
    warm = [v for v in vals if v <= 0.5]
    import math
    # nearest-rank percentile
    def pct(p):
        k = math.ceil(p / 100 * n)
        return vals[k - 1]
    print(f"{path}: n={n} cold={len(cold)}/20 warm={len(warm)}/20 "
          f"p50={pct(50):.3f}s min={vals[0]:.3f}s max={vals[-1]:.3f}s")
    if cold:
        print(f"   cold range: {min(cold):.3f}-{max(cold):.3f}s")
    if warm:
        print(f"   warm range: {min(warm):.3f}-{max(warm):.3f}s")

for p in sys.argv[1:]:
    stats(p)
