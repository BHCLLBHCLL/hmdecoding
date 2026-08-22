import glob, re
seen = set()
pats = [r"hm_getvalue\s+lines[^\n]{0,120}", r"hm_get\w*lines?[^\n]{0,100}", r"\*createmark\s+lines[^\n]{0,120}",
        r"hm_entityinfo[^\n]{0,100}", r"hm_getpoint[^\n]{0,80}"]
for pat in pats:
    rx = re.compile(pat, re.I)
    for f in glob.glob("C:/Program Files/Altair/2019/hm/scripts/**/*.tcl", recursive=True):
        try:
            data = open(f, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        for m in rx.finditer(data):
            h = m.group().strip()
            if h[:100] not in seen:
                seen.add(h[:100])
                print(f.split("\\")[-1], "::", h)
