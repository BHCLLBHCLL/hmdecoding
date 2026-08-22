import glob, re
seen = set()
pats = [r"\*createcurves?\s+[^\n]{0,100}", r"\*createlines?\s+[^\n]{0,100}", r"\*linecreate\s+[^\n]{0,80}", r"\*curves?\s+[^\n]{0,80}"]
for pat in pats:
    rx = re.compile(pat, re.I)
    for f in glob.glob("C:/Program Files/Altair/2019/hm/scripts/**/*.tcl", recursive=True):
        try:
            data = open(f, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        for m in rx.finditer(data):
            h = m.group().strip()
            if h[:80] not in seen:
                seen.add(h[:80])
                print(f.split("\\")[-1], "::", h)
