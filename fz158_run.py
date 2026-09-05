import json, subprocess, time, datetime

def curl(url, timeout=10):
    t0 = time.perf_counter()
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url, "--max-time", str(timeout)],
                       capture_output=True, text=True)
    ttfb = time.perf_counter() - t0
    return r.stdout.strip(), ttfb

def stats(times):
    ts = sorted(times)
    def pct(p):
        k = max(0, min(len(ts)-1, int(round(p/100*len(ts)))-1))
        return ts[k]
    cold = sum(1 for t in ts if t >= 0.5)
    return {"n": len(ts), "cold": cold, "p50": round(pct(50), 4), "p95": round(pct(95), 4), "max": round(max(ts), 4)}

SEARCH = "https://search.kotobase.net/search?q=test"
LANDING = "https://kotobase.net/"
out = {"ts": datetime.datetime.now().isoformat(), "runs": []}

for name in ["run158A", "run158B", "run158C"]:
    times = []
    codes = []
    for i in range(20):
        code, t = curl(SEARCH)
        codes.append(code)
        times.append(t)
    out["runs"].append({"name": name, "search": stats(times), "codes_ok": sum(1 for c in codes if c == "200")})

lc = []
lcode = []
for i in range(20):
    code, t = curl(LANDING)
    lcode.append(code)
    lc.append(t)
out["landing"] = stats(lc)
out["landing_ok"] = sum(1 for c in lcode if c == "200")

with open("fz158_out.json", "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out))
