import subprocess
d = "/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs"
out = []
for cmd in [["git", "fetch", "net-kotobase"],
            ["git", "rev-parse", "HEAD"],
            ["git", "rev-parse", "net-kotobase/main"],
            ["git", "merge-base", "--is-ancestor", "HEAD", "net-kotobase/main"],
            ["git", "log", "--oneline", "-3", "net-kotobase/main"]]:
    r = subprocess.run(cmd, cwd=d, capture_output=True, text=True)
    out.append("$ " + " ".join(cmd) + f" rc={r.returncode}\n" + (r.stdout or "") + (r.stderr or ""))
anc = "YES" if out[3].split("rc=1")[0].endswith("rc=0\n") else "NO"
open("/tmp/bench51_git_state.txt", "w").write("\n".join(out))
