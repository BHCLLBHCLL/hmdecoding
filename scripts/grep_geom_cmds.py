import glob, re
seen = set()
for cmd in (r"\*createpoint\s+[^\n]{0,100}", r"\*createline\s+[^\n]{0,100}", r"\*createcurve\s+[^\n]{0,100}"):
    pat = re.compile(cmd)
    for f in glob.glob("C:/Program Files/Altair/2019/hm/scripts/**/*.tcl", recursive=True):
        try:
            data = open(f, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        for m in pat.finditer(data):
            h = m.group().strip()
            if h[:90] not in seen:
                seen.add(h[:90])
                print(f.split("\\")[-1], "::", h)
