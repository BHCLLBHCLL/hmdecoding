import re
data = open("C:/Program Files/Altair/2019/hm/bin/win64/feconfig.cfg", encoding="utf-8", errors="replace").read()
# find lines mentioning config numbers / tetra / quad
lines = data.splitlines()
pats = re.compile(r"(tetra|quad|tria|hexa|config)", re.I)
for i, ln in enumerate(lines):
    if pats.search(ln) and len(ln) < 150:
        print(f"{i:5d} {ln}")
