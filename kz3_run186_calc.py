import re, statistics
txt = open("/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/kz3_run186_out.txt").read().splitlines()
blocks = {}
cur = None
for line in txt:
    if line.startswith("=== run"):
        cur = line.strip("= ").replace("run", "")
        blocks[cur] = []
    elif line.startswith("=== landing"):
        cur = "ctl"
        blocks[cur] = []
    elif line.strip() and cur:
        parts = line.split()
        blocks[cur].append((int(parts[0]), float(parts[1])*1000))
res = []
for k, v in blocks.items():
    codes = [c for c, t in v]
    times = sorted(t for c, t in v)
    cold = sum(1 for t in times if t > 500)
    p50 = statistics.median(times)
    res.append(f"{k}: n={len(v)} codes_ok={sum(1 for c in codes if c==200)}/{len(codes)} cold(>500ms)={cold} p50={p50:.1f}ms max={max(times):.1f}ms")
print("\n".join(res))
