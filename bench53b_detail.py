import json
d = json.load(open("bench53b_run163_out.json"))
for tag in ["A", "B", "C"]:
    seq = d[tag]["ttfb_ms"]
    colds = [t for t in seq if t >= 500]
    print("run163%s:" % tag, " ".join("%.0f" % t for t in seq))
    print("   colds:", " ".join("%.0f" % t for t in colds))
