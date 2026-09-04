import math

def parse_block(lines):
    vals = []
    for ln in lines:
        parts = ln.split()
        if len(parts) == 2 and parts[0] == "200":
            vals.append(float(parts[1]))
    return vals

def nearest_rank(vals, p):
    idx = max(1, math.ceil(p * len(vals)))
    return sorted(vals)[idx - 1]

def stats(vals):
    cold = [v for v in vals if v >= 0.5]
    warm = [v for v in vals if v < 0.5]
    return len(cold), (sorted(cold)[0], sorted(cold)[-1]) if cold else None, \
        nearest_rank(warm, 0.5) if warm else None, min(vals), max(vals)

out = open("kz3_run88_out.txt").read().split("=== ")
blocks = {}
for b in out[1:]:
    name, body = b.split(" ===", 1)
    blocks[name.strip()] = body.strip().splitlines()

for name in ["run88A search", "run88B search", "run88C search", "landing control"]:
    vals = parse_block(blocks[name])
    n = len(vals)
    cold_n, cold_rng, p50, mn, mx = stats(vals)
    print(f"{name}: n={n} cold={cold_n}/20 cold_range={cold_rng} warm_p50={p50}s min={mn}s max={mx}s")
