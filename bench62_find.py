import subprocess
out = subprocess.run(['grep','-n','-e','K-Q2','query-cosientist.md'],capture_output=True,text=True)
print('RC',out.returncode)
print(out.stdout[-3000:])
print(out.stderr[-500:])
out2 = subprocess.run(['grep','-n','-e','provision','query-cosientist.md'],capture_output=True,text=True)
print('RC2',out2.returncode)
print(out2.stdout[-3000:])
