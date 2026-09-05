import subprocess
for cmd in [
  ['bash','-lc','ls /Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase'],
  ['bash','-lc','grep -l "@noble" /Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs/*.mjs | head'],
  ['bash','-lc','find /Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase -maxdepth 3 -name "package.json" -not -path "*/node_modules/*" | head'],
]:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    print('CMD', cmd[-1], 'RC', r.returncode)
    print(r.stdout[:2000])
    if r.stderr: print('ERR', r.stderr[:500])
