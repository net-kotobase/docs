import subprocess, json

def run(cmd, timeout=120):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd='/Users/junkawasaki/github/com-junkawasaki/orgs/net-kotobase/docs')
    return (p.stdout + p.stderr).strip()

# Probe: TTFB vs total (time_total) decomposition + curl HTTP version/IP, on both search and landing.
# This distinguishes (a) TTFB-heavy origin slowness vs (b) connection/TLS establishment cost.
lines = []
urls = {
    'search': 'https://search.kotobase.net/search?q=test',
    'landing': 'https://kotobase.net/',
}
for label, url in urls.items():
    for i in range(3):
        p = subprocess.run(
            ['curl', '-o', '/dev/null', '-s', '-w',
             '%{http_code} ttfb=%{time_starttransfer} total=%{time_total} dns=%{time_namelookup} conn=%{time_connect} tls=%{time_appconnect} ip=%{remote_ip} http=%{http_version}\n',
             '--max-time', '10', url],
            capture_output=True, text=True, timeout=15)
        lines.append(f'{label}#{i+1}: {p.stdout.strip()}')

# Check cold sample detail in past run outputs: was TTFB elevated, or total elevated with fast TTFB?
open('/tmp/fz_state5.txt', 'w').write('\n'.join(lines))
print('ok')
