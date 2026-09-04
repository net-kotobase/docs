import re, statistics, sys

path = sys.argv[1]
blocks = []
cur = None
for line in open(path):
    m = re.match(r"=== (run\w+) search", line)
    if m:
        cur = {"id": m.group(1), "vals": [], "codes": []}
        blocks.append(cur)
        continue
    if line.startswith("=== landing control"):
        cur = {"id": "control", "vals": [], "codes": []}
        blocks.append(cur)
        continue
    m = re.match(r"(\d{3}) ([\d.]+)", line.strip())
    if m and cur:
        cur["codes"].append(int(m.group(1)))
        cur["vals"].append(float(m.group(2)))

tot = 0
tot_cold = 0
for b in blocks:
    vals = sorted(b["vals"])
    n = len(vals)
    cold = [v for v in vals if v >= 0.5]
    warm = [v for v in vals if v < 0.5]
    p50 = vals[max(0, (n + 1) // 2 - 1)]
    codes_ok = all(c == 200 for c in b["codes"])
    tot += n
    tot_cold += len(cold)
    if cold:
        print(f"{b['id']}: n={n} 200={codes_ok} cold={len(cold)} ({min(cold):.2f}-{max(cold):.2f}s) warm {len(warm)} p50={p50:.3f}s range={vals[0]:.3f}-{vals[-1]:.3f}")
    else:
        print(f"{b['id']}: n={n} 200={codes_ok} cold=0 p50={p50:.3f}s range={vals[0]:.3f}-{vals[-1]:.3f}")
print(f"TOTAL: n={tot} cold>0={tot_cold}")
