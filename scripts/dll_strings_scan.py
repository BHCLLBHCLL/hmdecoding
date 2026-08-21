import re, sys, glob
paths = glob.glob(sys.argv[1])
pats = re.compile(r"(?i)(gzip|deflate|zlib|compress|.hm\\b|hmbin|hmbinary|database|header|footer|version)", re.I)
for p in paths:
    try:
        data = open(p, "rb").read()
    except Exception as e:
        print(p, "ERR", e); continue
    strings = {}
    for m in re.finditer(rb"[ -~]{6,}", data):
        s = m.group().decode("ascii", "replace")
        if re.search(r"[A-Za-z]{3}", s):
            strings.setdefault(s, 0); strings[s] += 1
    hits = sorted([s for s in strings if pats.search(s)], key=lambda s: -len(s))
    if hits:
        print("=" * 20, p, len(data), "bytes")
        for s in hits[:25]:
            print(f"  {strings[s]:3d}x  {s[:100]}")
