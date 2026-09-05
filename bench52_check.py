import subprocess
r = subprocess.run(["date"], capture_output=True, text=True)
print("rc", r.returncode, r.stdout, r.stderr)
