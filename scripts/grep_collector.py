import glob, re
seen = set()
for f in glob.glob("C:/Program Files/Altair/2019/hm/scripts/**/*.tcl", recursive=True):
    try:
        data = open(f, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    for m in re.finditer(r"\*createcollector\s+[^\n]{0,100}", data):
        h = m.group().strip()
        if h[:70] not in seen:
            seen.add(h[:70])
            print(f.split("\\")[-1], "::", h)
