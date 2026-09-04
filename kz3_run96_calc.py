import re, statistics
txt = open('kz3_run96_out.txt').read().splitlines()
runs, cur = {}, None
for line in txt:
    m = re.match(r'=== (.+) ===', line)
    if m: cur = m.group(1); runs[cur] = []
    elif line.startswith('200') and cur:
        runs[cur].append(float(line.split()[1]))
for name, vals in runs.items():
    s = sorted(vals)
    p50 = s[len(s)//2]
    cold = sum(1 for v in s if v >= 0.5)
    print(f"{name}: n={len(s)} cold(>=0.5s) {cold}/{len(s)} p50 {p50:.3f}s min {s[0]:.3f} max {s[-1]:.3f}")
