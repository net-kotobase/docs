import io, json, subprocess, time, datetime

BASE = "https://search.kotobase.net/search?q=test"
CONTROL = "https://kotobase.net/"
N = 20
COLD_MS = 500.0
TICK = 300  # */5 cron period in seconds

def nearest_rank(sorted_s, p):
    return sorted_s[max(0, int(-(-p*len(sorted_s)//1)) - 1)]

def curl_time(url):
    fmt = "%{time_starttransfer} %{time_total} %{http_code}"
    r = subprocess.run(["/usr/bin/curl", "-s", "-o", "/dev/null", "-w", fmt, "--max-time", "10", url],
                       capture_output=True, text=True)
    parts = r.stdout.strip().split()
    return float(parts[0]), float(parts[1]), int(parts[2])

def measure(url, n):
    ttfbs = []
    codes = []
    for i in range(n):
        ttfb, total, code = curl_time(url)
        ttfbs.append(ttfb)
        codes.append(code)
        time.sleep(0.2)
    cold = [t for t in ttfbs if t >= 0.5]
    warm = sorted(t for t in ttfbs if t < 0.5)
    s = sorted(ttfbs)
    return {
        "n": n,
        "codes_ok": sum(1 for c in codes if c == 200),
        "cold_count": len(cold),
        "cold_range": [min(cold), max(cold)] if cold else None,
        "cold_positions": [i + 1 for i, t in enumerate(ttfbs) if t >= 0.5],
        "warm_count": len(warm),
        "p50_all": s[n//2 - 1],
        "warm_p50": nearest_rank(warm, 0.5) if len(warm) >= 2 else None,
        "warm_min": min(warm) if warm else None,
        "warm_max": max(warm) if warm else None,
        "ttfbs": ttfbs,
    }

def nowsec():
    n = datetime.datetime.now().astimezone()
    return n.hour * 3600 + n.minute * 60 + n.second

def nowstr():
    return datetime.datetime.now().astimezone().strftime("%H:%M:%S")

# --- wait until just after the next */5 fire ---
t0 = nowsec()
phase = t0 % TICK
if phase <= 45:  # within 45s after a fire: start immediately (direct-after window)
    fired_at = nowstr()
    waited = 0
else:
    to_wait = TICK - phase + 3  # fire + 3s
    time.sleep(to_wait)
    fired_at = nowstr()
    waited = to_wait

run_direct = measure(BASE, N)
elapsed0 = nowstr()

# elapsed run: start ~90s after fire (run11-style contrast)
target = nowsec() + 90 - (nowsec() - (t0 if waited == 0 else t0 + waited))
# simpler: absolute target = fire_epoch + 90
# recompute fire epoch: use wall clock
import datetime as _dt
def epoch():
    return time.time()
# fired_at was recorded right after fire, so fire_epoch ~ epoch() - (now - fired)
direct_dur = nowsec() - nowsec()  # placeholder
# compute directly: we know elapsed0 == direct end; elapsed target = direct_start + 90
# direct_start = fired_at (string) -> approximate via wall clock at loop entry
# do it robustly: track wall clock at fire moment
# (fired_at captured within ~0.1s of fire)
# So:
# fire_epoch ~ time.time() - (seconds since fired_at)
# We stored nothing; recompute from now: direct started at 'fired_at'; we need +90s from then.
# Track it explicitly:
# (see below - use time_monotonic style approach instead)

# Since we lost the exact fire epoch, approximate: elapsed run starts when wall clock
# reaches (start of direct run + 90s). start of direct run = fired_at.
fh, fm, fs = (int(x) for x in fired_at.split(":"))
fire_abs = fh * 3600 + fm * 60 + fs
# handle midnight rollover
now_abs = nowsec()
if fire_abs > now_abs:  # rolled past midnight during run
    fire_abs -= 86400
target_abs = fire_abs + 90
while nowsec() < target_abs and nowsec() - fire_abs < 150:
    time.sleep(2)

run_elapsed = measure(BASE, N)
elapsed_end = nowstr()

cttfb, ctotal, ccode = curl_time(CONTROL)
load_line = subprocess.run(["/usr/bin/uptime"], capture_output=True, text=True).stdout.strip()

out = {
    "fired_at": fired_at,
    "direct_after_s": "fire+3s (or immediate if phase<=45)",
    "elapsed_start": elapsed0,
    "elapsed_end": elapsed_end,
    "load": load_line,
    "runs": [{"name": "direct-after", **run_direct}, {"name": "elapsed", **run_elapsed}],
    "control": {"ttfb": cttfb, "code": ccode},
}
with open("/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/bench38_out.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
with open("/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/bench38_out.txt", "w") as f:
    f.write("fired_at=%s elapsed=%s-%s\n%s\n" % (fired_at, elapsed0, elapsed_end, load_line))
    for r in out["runs"]:
        f.write("%s ok=%d/%d cold=%d/%d cold_range=%s cold_pos=%s warm_p50=%s p50_all=%s\n" % (
            r["name"], r["codes_ok"], r["n"], r["cold_count"], r["n"],
            r["cold_range"], r["cold_positions"], r["warm_p50"], r["p50_all"]))
    f.write("control ttfb=%s code=%s\n" % (cttfb, ccode))
print("done", fired_at, elapsed_end)
