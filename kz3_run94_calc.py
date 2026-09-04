import sys

def p50_nearest_rank(xs):
    xs = sorted(xs)
    import math
    return xs[math.ceil(0.5 * len(xs)) - 1]

for name in ["run94A", "run94B", "run94C", "control"]:
    vals = []
    with open("kz3_run94_out.txt") as f:
        section = None
        for line in f:
            line = line.strip()
            if line.startswith("=== run94A"):
                section = "run94A"
            elif line.startswith("=== run94B"):
                section = "run94B"
            elif line.startswith("=== run94C"):
                section = "run94C"
            elif line.startswith("=== landing"):
                section = "control"
            elif line and section == name:
                parts = line.split()
                vals.append((int(parts[0]), float(parts[1])))
    codes = [c for c, _ in vals]
    tt = [t for _, t in vals]
    cold = [t for t in tt if t >= 0.5]
    print(f"{name}: n={len(vals)} non200={codes.count(200)} is-all-200={all(c==200 for c in codes)} cold>=0.5s={len(cold)} coldvals={[round(t,3) for t in cold]} p50={p50_nearest_rank(tt):.3f} min={min(tt):.3f} max={max(tt):.3f}")
