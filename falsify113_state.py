import subprocess, sys

def run(cmd, timeout=120):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd='/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs')
    return (p.stdout + p.stderr).strip()

out = []
out.append('=== NEXT ===')
out.append(run("grep -n 'NEXT' query-cosientist.md | tail -5"))
out.append('')
out.append('=== K-Z2 row ===')
out.append(run("grep -n 'K-Z2' query-cosientist.md | head -5"))
out.append('')
out.append('=== K-Z3 row ===')
out.append(run("grep -n 'K-Z3' query-cosientist.md | head -5"))
out.append('')
out.append('=== remote net-kotobase? ===')
out.append(run("git remote -v"))
out.append('')
out.append('=== fetch ===')
out.append(run("git fetch net-kotobase 2>&1 | tail -3; git log --oneline net-kotobase/main -5"))
open('/tmp/fz_state.txt', 'w').write('\n'.join(out))
print('done')
