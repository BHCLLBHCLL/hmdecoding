import glob, re
hits = []
for pat in ["C:/Program Files/Altair/2019/hm/scripts/**/*.tcl",
            "C:/Program Files/Altair/2019/hm/scripts/**/*.cmd",
            "C:/Program Files/Altair/2019/hm/scripts/**/*.mac",
            "C:/Program Files/Altair/2019/hm/templates/**/*",
            "C:/Program Files/Altair/2019/hm/bin/win64/*.mac"]:
    for f in glob.glob(pat, recursive=True):
        try:
            data = open(f, "rb").read()
        except Exception:
            continue
        for m in re.finditer(rb"\*createelement\s+[^\n]{0,120}", data):
            hits.append((f, m.group().decode("ascii", "replace")))
print("createelement usages:", len(hits))
seen = set()
for f, h in hits[:40]:
    key = h[:80]
    if key in seen: continue
    seen.add(key)
    print(f.split("\\")[-1], "::", h)
