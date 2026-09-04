import re, statistics
runs = {"86A": [], "86B": [], "86C": [], "L": []}
cur = None
data = open("kz3_run86_out.txt").read().splitlines()
for line in data:
    m = re.match(r"=== (\S+)", line)
    if m:
        rid = m.group(1)
        cur = "L" if "landing" in rid else rid.replace("run", "")
        continue
    parts = line.split()
    if len(parts) != 2 or cur is None:
        continue
    code, t = parts
    runs[cur].append((code, float(t)))
for rid, vals in runs.items():
    ts = sorted(v for c, v in vals)
    n = len(ts)
    p50 = ts[max(0, -(-n*50//100)-1)]
    cold = sum(1 for c, v in vals if c != "200" or v > 0.5)
    non200 = [c for c, v in vals if c != "200"]
    print(rid, "n=", n, "p50=", round(p50,3), "cold>0.5s=", cold, "non200=", non200)
