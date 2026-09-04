import subprocess

def run(cmd, timeout=60):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd='/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs')
    return (p.stdout + p.stderr).strip()

out = []
out.append(run("grep -n 'run114' query-cosientist.md | head -3"))
out.append('---')
out.append(run("grep -n '^| K-Z2 |' query-cosientist.md | cut -d: -f1"))
out.append('---')
out.append(run("git diff --stat query-cosientist.md"))
open('/tmp/fz_verify114.txt', 'w').write('\n'.join(out))
print('ok')
