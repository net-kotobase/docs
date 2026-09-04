def p50_nearest(sorted_vals):
    import math
    n = len(sorted_vals)
    idx = math.ceil(0.5 * n) - 1
    return sorted_vals[idx]

def load(path, section):
    vals = []
    inside = False
    for line in open(path):
        line = line.strip()
        if line.startswith("==="):
            inside = section in line
            continue
        if inside and line:
            code, t = line.split()
            vals.append((code, float(t)))
    return vals

for rid in ["run90A", "run90B", "run90C", "landing control"]:
    vals = load("kz3_run90_out.txt", rid)
    times = sorted(t for c, t in vals)
    cold = [t for c, t in vals if t >= 0.5]
    ok = sum(1 for c, t in vals if c == "200")
    print(f"{rid}: n={len(vals)} 200s={ok} cold(>=0.5s)={len(cold)} "
          f"cold_range={min(cold) if cold else '-'}-{max(cold) if cold else '-'} "
          f"p50={p50_nearest(times):.3f} min={times[0]:.3f} max={times[-1]:.3f}")
