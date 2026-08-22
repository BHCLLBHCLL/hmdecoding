import gzip, struct, re
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
            blocks.append((m.group().decode("ascii", "replace"), cid))
    return blocks
files = {}
cur = None
for line in open("output/ground_truth/gt_extended.log", encoding="utf-8").read().splitlines():
    line = line.strip()
    if line.startswith("==FILE== "):
        cur = line[len("==FILE== "):]
        files[cur] = defaultdict(list)
    elif line.startswith("comps id=") and cur:
        files[cur]["comps"].append(line.split("name=")[1])
    elif line.startswith("mats id=") and cur:
        files[cur]["mats"].append(line.split("name=")[1])
    elif line.startswith("props id=") and cur:
        files[cur]["props"].append(line.split("name=")[1])
stats = defaultdict(lambda: defaultdict(int))
for path, data in files.items():
    try:
        raw = open(path, "rb").read()
        payload = gzip.decompress(raw[12:])
    except Exception:
        continue
    for name, cid in named_blocks(payload):
        ents = set()
        for ent in ("comps", "mats", "props"):
            if name in data.get(ent, []):
                ents.add(ent)
        if not ents:
            ents = {"?"}
        for ent in ents:
            stats[cid][ent] += 1
out = []
out.append(f"{'cid':>4} {'comps':>6} {'mats':>6} {'props':>6} {'?':>5}  解读")
for cid in sorted(stats):
    s = stats[cid]
    tot = sum(s.values())
    ent = max(s, key=s.get)
    out.append(f"{cid:>4} {s.get('comps',0):>6} {s.get('mats',0):>6} {s.get('props',0):>6} {s.get('?',0):>5}  -> {ent} ({tot})")
open("output/ground_truth/classid_result3.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
