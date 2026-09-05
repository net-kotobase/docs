import json, subprocess, time, statistics, datetime

N = 20
COLD = 0.5
SEARCH = "https://search.kotobase.net/search?q=test"
LANDING = "https://kotobase.net/"

def run_seq(url, n=N):
    ttfbs = []
    codes = []
    for _ in range(n):
        r = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code} %{time_total}",
             "--max-time", "15", url],
            capture_output=True, text=True)
        out = r.stdout.strip()
        code, t = out.split()
        codes.append(code)
        ttfbs.append(float(t) * 1000.0)
    return ttfbs, codes

def stats(ttfbs):
    s = sorted(ttfbs)
    cold50 = sum(1 for t in s if t >= COLD * 1000)
    cold1 = sum(1 for t in s if t >= 1000)
    p50 = s[max(0, int(round(0.50 * len(s) + 0.5)) - 1)]
    return cold50, cold1, p50, s[0], s[-1]

results = {}
for tag, url in [("A", SEARCH), ("B", SEARCH), ("C", SEARCH), ("landing", LANDING)]:
    ttfbs, codes = run_seq(url)
    c50, c1, p50, lo, hi = stats(ttfbs)
    results[tag] = {"codes": codes, "ttfb_ms": [round(t, 1) for t in ttfbs],
                    "cold_ge_500ms": c50, "cold_ge_1s": c1,
                    "p50_ms": round(p50, 1), "min_ms": round(lo, 1), "max_ms": round(hi, 1)}

now = datetime.datetime.now().astimezone()
results["time"] = now.isoformat()
with open("bench53b_run163_out.json", "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)

for tag in ["A", "B", "C", "landing"]:
    r = results[tag]
    print("run163%s (%s): all200=%s cold(>=0.5s) %d/20 cold(>=1s) %d/20 p50 %.1fms min %.1f max %.1f" % (
        tag, "search" if tag != "landing" else "landing control",
        all(c == "200" for c in r["codes"]), r["cold_ge_500ms"], r["cold_ge_1s"],
        r["p50_ms"], r["min_ms"], r["max_ms"]))
print("time:", results["time"])
