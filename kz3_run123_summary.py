import re, statistics, json

path = "/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/kz3_run123_out.txt"
runs = {}
current = None
with open(path) as f:
    for line in f:
        line = line.strip()
        m = re.match(r"=== (run\w+|landing control)", line)
        if m:
            current = m.group(1)
            runs[current] = []
            continue
        m = re.match(r"^(\d{3}) ([\d.]+)$", line)
        if m and current:
            runs[current].append((m.group(1), float(m.group(2))))

report = {}
for rid, samples in runs.items():
    codes = [c for c, _ in samples]
    times = [t for _, t in samples]
    cold = [t for t in times if t >= 0.5]
    s = sorted(times)
    def pct(p):
        k = (len(s) - 1) * p
        f0 = int(k)
        c0 = min(f0 + 1, len(s) - 1)
        return s[f0] + (s[c0] - s[f0]) * (k - f0)
    report[rid] = {
        "n": len(samples),
        "codes_all_200": all(c == "200" for c in codes),
        "cold_count": len(cold),
        "p50_ms": round(pct(0.5) * 1000, 1),
        "p90_ms": round(pct(0.9) * 1000, 1),
        "max_ms": round(max(times) * 1000, 1),
        "min_ms": round(min(times) * 1000, 1),
        "cold_values_s": [round(t, 3) for t in cold],
    }

print(json.dumps(report, indent=1))
