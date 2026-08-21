import glob, gzip, struct, os
from collections import defaultdict
cands = sorted(glob.glob("C:/Program Files/Altair/2019/tutorials/hm/**/*.hm", recursive=True))
cands += sorted(glob.glob("C:/Program Files/Altair/2019/tutorials/hm/**/*.hm10", recursive=True))
tab = defaultdict(list)
for f in cands:
    raw = open(f, "rb").read()
    payload = gzip.decompress(raw[12:])
    v = round(struct.unpack("<d", payload[4:12])[0], 2)
    w14 = struct.unpack("<I", payload[0x14:0x18])[0]
    w1c = struct.unpack("<I", payload[0x1c:0x20])[0]
    c40 = struct.unpack("<I", payload[0x3c:0x40])[0]
    tab[v].append((w14, w1c, c40, os.path.basename(f)))
print(f"{'ver':>6} {'n':>4} | w14 values | w1c values | w3c values")
for v in sorted(tab):
    items = tab[v]
    from collections import Counter
    w14s = Counter(i[0] for i in items)
    w1cs = Counter(i[1] for i in items)
    w3cs = Counter(i[2] for i in items)
    print(f"{v:>6} {len(items):>4} | {dict(w14s)} | {dict(w1cs)} | {dict(w3cs)}")
    for i in items[:2]:
        print(f"         e.g. {i[3]}")
