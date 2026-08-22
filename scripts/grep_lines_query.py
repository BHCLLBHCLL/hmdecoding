import glob, re
seen = set()
pats = re.compile(r"hm_getvalue\s+lines\s+[^\n]{0,120}", re.I)
for f in glob.glob("C:/Program Files/Altair/2019/hm/scripts/**/*.tcl", recursive=True):
    try:
        data = open(f, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    for m in pats.finditer(data):
        h = m.group().strip()
        if h[:100] not in seen:
            seen.add(h[:100])
            print(f.split("\\")[-1], "::", h)
