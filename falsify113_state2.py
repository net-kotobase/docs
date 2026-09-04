import subprocess

def run(cmd, timeout=120):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd='/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs')
    return (p.stdout + p.stderr).strip()

out = []
out.append(run("git checkout net-kotobase/main 2>&1 | tail -2; git status -sb | head -3"))
out.append('--- K-Z3 latest evidence (tail) ---')
out.append(run("grep -n 'K-Z3' query-cosientist.md | tail -3"))
out.append('--- run112 evidence lines ---')
out.append(run("grep -n 'run112' query-cosientist.md | tail -4"))
out.append('--- bench38 harness check ---')
out.append(run("ls ../biscuit-auth-query-bench/authn/scripts/live_biscuit_query_bench.mjs"))
open('/tmp/fz_state2.txt', 'w').write('\n'.join(out))
print('ok')
