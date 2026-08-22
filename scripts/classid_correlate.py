import gzip, struct, re, json
from collections import defaultdict

def u32(p, o): return struct.unpack_from("<I", p, o)[0]

def named_blocks(payload):
    blocks = []
    for m in re.finditer(rb"[A-Za-z_][A-Za-z0-9_]{1,31}", payload):
        s = m.start()
        if s < 12:
            continue
        cap = u32(payload, s - 12)
        zw = u32(payload, s - 8)
        cid = u32(payload, s - 4)
        if 4 <= cap <= 64 and zw == 0 and 0 < cid <= 64:
            blocks.append((s - 12, m.group().decode("ascii", "replace"), cid))
    return blocks

gt = json.load(open("output/ground_truth/corpus_gt.json", encoding="utf-8"))
selected = []
for path, data in gt.items():
    counts = data.get("counts", {})
    if counts.get("nodes", 0) > 0 and counts.get("comps", 0) > 0:
        selected.append(path)
selected = selected[:14]
stats = defaultdict(lambda: defaultdict(int))
detail = defaultdict(list)
for path in selected:
    try:
        raw = open(path, "rb").read()
        payload = gzip.decompress(raw[12:])
    except Exception:
        continue
    blocks = named_blocks(payload)
    data = gt[path]
    known = {}
    for ent in ("comps", "mats", "props"):
        for item in data.get(ent, []):
            known[item["name"]] = ent
    for off, name, cid in blocks:
        ent = known.get(name, "UNKNOWN")
        stats[cid][ent] += 1
        detail[cid].append((name, ent))
out = []
for cid in sorted(stats):
    s = stats[cid]
    total = sum(s.values())
    ent = max(s, key=s.get) if s else "?"
    out.append(f"class_id {cid}: comp={s.get('comp',0)} mat={s.get('mat',0)} prop={s.get('prop',0)} unknown={s.get('UNKNOWN',0)} total={total} -> {ent}")
    names = sorted(set(n for n, e in detail[cid] if e != "UNKNOWN"))[:6]
    out.append(f"    known names: {names}")
open("output/ground_truth/classid_result.txt", "w", encoding="utf-8").write("\n".join(out))
print("written", len(out), "lines")
