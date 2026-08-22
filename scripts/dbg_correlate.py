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
# parse extended log for 1d_elements
import os
files = {}
cur = None
for line in open("output/ground_truth/gt_extended.log", encoding="utf-8").read().splitlines():
    line = line.strip()
    if line.startswith("==FILE== "):
        cur = line[len("==FILE== "):]
        files[cur] = defaultdict(list)
    elif line.startswith("count ") and cur:
        parts = line.split()
        files[cur]["_c_" + parts[1].rstrip(":")] = int(parts[2])
    elif line.startswith("comps id=") and cur:
        files[cur]["comps"].append(line.split("name=")[1])
    elif line.startswith("mats id=") and cur:
        files[cur]["mats"].append(line.split("name=")[1])
    elif line.startswith("props id=") and cur:
        files[cur]["props"].append(line.split("name=")[1])
target = [p for p in files if p.endswith("1d_elements.hm")][0]
print("target:", target)
print("comps:", files[target]["comps"])
print("mats:", files[target]["mats"])
print("props:", files[target]["props"])
raw = open(target, "rb").read()
p = gzip.decompress(raw[12:])
blocks = named_blocks(p)
known = {}
for ent in ("comps", "mats", "props"):
    for nm in files[target].get(ent, []):
        known[nm] = ent
print("known:", known)
for name, cid in blocks:
    print(f"  {name!r} cid={cid} -> {known.get(name, '?')}")
