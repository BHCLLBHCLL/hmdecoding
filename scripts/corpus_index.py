import glob, gzip, struct, os, json
from collections import Counter
cands = sorted(glob.glob("C:/Program Files/Altair/2019/tutorials/hm/**/*.hm", recursive=True))
cands += sorted(glob.glob("C:/Program Files/Altair/2019/tutorials/hm/**/*.hm10", recursive=True))
def layout_family(w14, w1c):
    if w14 == 126: return "v11-classic"
    if w14 == 10000: return "v12-13"
    if w14 == 1: return "v14+"
    return "v10-legacy"
rows = []
for f in cands:
    raw = open(f, "rb").read()
    payload = gzip.decompress(raw[12:])
    v = round(struct.unpack("<d", payload[4:12])[0], 2)
    w14 = struct.unpack("<I", payload[0x14:0x18])[0]
    w1c = struct.unpack("<I", payload[0x1c:0x20])[0]
    w3c = struct.unpack("<I", payload[0x3c:0x40])[0]
    rows.append({
        "relpath": os.path.relpath(f, "C:/Program Files/Altair/2019/tutorials/hm").replace("\\", "/"),
        "abs": f.replace("\\", "/"),
        "compressed": len(raw),
        "payload": len(payload),
        "db_version": v,
        "layout": layout_family(w14, w1c),
        "w14": w14, "w1c": w1c, "w3c": w3c,
    })
os.makedirs("corpus", exist_ok=True)
json.dump(rows, open("corpus/corpus_index.json", "w"), indent=1)
fam = Counter(r["layout"] for r in rows)
ver = Counter(r["db_version"] for r in rows)
print("indexed:", len(rows))
print("layout families:", dict(fam))
print("versions:", dict(sorted(ver.items())))
tot = sum(r["payload"] for r in rows)
print("total payload bytes:", tot)
# curated tiny representatives per family
for fl in sorted(set(r["layout"] for r in rows)):
    reps = sorted([r for r in rows if r["layout"] == fl], key=lambda r: r["compressed"])[:2]
    for r in reps:
        print(f"  tiny rep [{fl}] {r['relpath']} compressed={r['compressed']} payload={r['payload']} v{r['db_version']}")
