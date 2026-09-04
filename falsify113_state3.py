import subprocess

def run(cmd, timeout=120):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd='/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs')
    return (p.stdout + p.stderr).strip()

out = []
out.append('=== query repo wrangler/routes ===')
out.append(run("ls ../ | head -20"))
out.append(run("find ../ -maxdepth 3 -name 'wrangler.toml' -o -maxdepth 3 -name 'wrangler.jsonc' -o -maxdepth 3 -name 'wrangler.json' 2>/dev/null | head -10"))
out.append(run("grep -rn 'workers.dev' ../ --include=wrangler.toml --include=wrangler.jsonc --include='*.md' -l 2>/dev/null | head -10"))
open('/tmp/fz_state3.txt', 'w').write('\n'.join(out))
print('ok')
