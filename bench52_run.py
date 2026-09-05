import subprocess
d = "/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs"
r = subprocess.run(["node", "bench52_kq1_edge.mjs"],
                   cwd=d, capture_output=True, text=True, timeout=300)
open("bench52_kq1_out.json", "w").write(r.stdout or "")
open("bench52_kq1_err.txt", "w").write((r.stderr or "") + f"\nrc={r.returncode}\n")
print("rc", r.returncode)
