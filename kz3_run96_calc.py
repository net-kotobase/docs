import re, statistics

def p50_nearest_rank(xs):
    xs = sorted(xs)
    import math
    k = math.ceil(0.5 * len(xs))
    return xs[k - 1]

for block in ["96A", "96B", "96C", "ctrl"]:
    vals = []
    with open("kz3_run96_out.txt") as f:
        lines = f.read().splitlines()
    cur = None
    for ln in lines:
        m = re.match(r"=== (run\S+|landing control)", ln)
        if m:
            cur = m.group(1)
            continue
        code, t = ln.split()
        key = {"96A": "run96A", "96B": "run96B", "96C": "run96C"}.get(cur, "ctrl") if cur else "ctrl"
        if key == block:
            vals.append(float(t))
    cold = [v for v in vals if v > 0.5]
    warm = [v for v in vals if v <= 0.5]
    print(f"{block}: n={len(vals)} cold={len(cold)}/20 {['%.3f' % v for v in cold]} warmP50={p50_nearest_rank(warm):.3f} warmRange={min(warm):.3f}-{max(warm):.3f}")
