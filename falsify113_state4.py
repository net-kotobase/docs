import subprocess

def run(cmd, timeout=120):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd='/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs')
    return (p.stdout + p.stderr).strip()

out = []
out.append('=== gateway routes ===')
out.append(run("grep -n 'kotobase.net\\|route\\|search' ../sdk/gateway/wrangler.jsonc | head -20"))
out.append('=== search-origin routes ===')
out.append(run("grep -n 'kotobase.net\\|route\\|search' ../search-origin/wrangler.jsonc | head -20"))
open('/tmp/fz_state4.txt', 'w').write('\n'.join(out))
print('ok')
