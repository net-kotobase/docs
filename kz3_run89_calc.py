import re

lines = open("kz3_run89_out.txt").read().splitlines()
section = None
runs = {}
order = []
for ln in lines:
    m = re.match(r"== (run89[A-C]|landing control).*", ln)
    if m:
        section = m.group(1)
        runs[section] = []
        order.append(section)
        continue
    m = re.match(r"\d+ (\d{3}) ([\d.]+)", ln)
    if m and section:
        runs[section].append((int(m.group(1)), float(m.group(2))))

for name in order:
    rows = runs[name]
    codes = [c for c, _ in rows]
    tt = sorted(t for _, t in rows)
    cold = [t for _, t in rows if t >= 0.5]
    p50 = tt[len(tt) // 2 - 1] if len(tt) % 2 == 0 else tt[len(tt) // 2]
    print(f"{name}: n={len(rows)} all200={all(c == 200 for c in codes)} "
          f"cold(>=0.5s) {len(cold)}/{len(rows)} "
          f"({min(cold):.3f}-{max(cold):.3f}s)" if cold else
          f"{name}: n={len(rows)} all200={all(c == 200 for c in codes)} cold 0/{len(rows)}",
          f"p50={p50:.3f}s min={tt[0]:.3f} max={tt[-1]:.3f}")
