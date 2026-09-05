import json, subprocess, time, datetime

def curl(url):
    t0 = time.perf_counter()
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url, "--max-time", "10"],
                       capture_output=True, text=True)
    return r.stdout.strip(), time.perf_counter() - t0

out = {"ts": datetime.datetime.now().isoformat()}
for name, url in [("landing2", "https://kotobase.net/"), ("search2", "https://search.kotobase.net/search?q=test")]:
    times = []; codes = []
    for i in range(20):
        c, t = curl(url); codes.append(c); times.append(t)
    ts = sorted(times)
    out[name] = {"ok": sum(1 for c in codes if c == "200"), "cold": sum(1 for t in ts if t >= 0.5),
                 "p50": round(ts[9], 4), "min": round(ts[0], 4), "max": round(ts[-1], 4)}
with open("fz158b_out.json", "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out))
