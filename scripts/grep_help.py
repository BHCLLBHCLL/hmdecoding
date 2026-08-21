import glob, re
# find Tcl command reference files
cands = glob.glob("C:/Program Files/Altair/2019/hm/html/**/*.htm*", recursive=True) + glob.glob("C:/Program Files/Altair/2019/help/**/*", recursive=True)
print("candidates:", len(cands))
pats = [r"createcollector", r"createnode", r"createelement"]
for pat in pats:
    hits = 0
    for f in cands:
        try:
            data = open(f, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        for m in re.finditer(pat, data, re.I):
            if hits < 3:
                i = m.start()
                ctx = data[max(0, i-100):i+300].replace("\n", " ")
                ctx = re.sub(r"<[^>]+>", "", ctx)
                print(f"[{pat}] {f.split(chr(92))[-1]}: ...{ctx[:300]}...")
            hits += 1
    print(f"  {pat}: {hits} hits")
