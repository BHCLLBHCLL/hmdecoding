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
    elif line.startswith("count ") and cur:
        parts = line.split()
        files[cur]["_counts_" + parts[1].rstrip(":")] = int(parts[2])
    elif line.startswith("comps id=") and cur:
        files[cur]["comps"].append(line.split("name=")[1])
    elif line.startswith("mats id=") and cur:
        files[cur]["mats"].append(line.split("name=")[1])
    elif line.startswith("props id=") and cur:
        files[cur]["props"].append(line.split("name=")[1])
    elif line.startswith("systems id=") and cur:
        files[cur]["systems"].append(line.split("name=")[1])
    elif line.startswith("groups id=") and cur:
        files[cur]["groups"].append(line.split("name=")[1])
    elif line.startswith("loads id=") and cur:
        files[cur]["loads"].append(line.split("name=")[1])

stats = defaultdict(lambda: defaultdict(int))
name2cid = defaultdict(set)
for path, data in files.items():
    try:
        raw = open(path, "rb").read()
        payload = gzip.decompress(raw[12:])
    except Exception:
        continue
    known = {}
    for ent in ("comps", "mats", "props", "systems", "groups", "loads"):
        for nm in data.get(ent, []):
            known[nm] = ent
    for name, cid in named_blocks(payload):
        ent = known.get(name, "?")
        stats[cid][ent] += 1
        name2cid[name].add(cid)
out = []
out.append(f"{'cid':>4} {'comp':>5} {'mat':>5} {'prop':>5} {'sys':>4} {'grp':>4} {'load':>5} {'?':>4}  解读")
for cid in sorted(stats):
    s = stats[cid]
    tot = sum(s.values())
    ent = max(s, key=s.get)
    out.append(f"{cid:>4} {s.get('comp',0):>5} {s.get('mat',0):>5} {s.get('prop',0):>5} {s.get('systems',0):>4} {s.get('groups',0):>4} {s.get('loads',0):>5} {s.get('?',0):>4}  -> {ent} ({tot})")
multi = {n: c for n, c in name2cid.items() if len(c) > 1}
out.append("")
out.append(f"名字冲突: {len(multi)}")
for n, c in list(multi.items())[:10]:
    out.append(f"  {n}: {sorted(c)}")
open("output/ground_truth/classid_result2.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
