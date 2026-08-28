"""config 1/22/61 分析: 搜节点 ID 的 u32 位置, 看与 eid 的关系."""
import sys, struct, re
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")

def find_all(val, as_u32=True):
    pat = struct.pack("<I" if as_u32 else "<H", val)
    out = []
    j = 0
    while True:
        j = p.find(pat, j)
        if j < 0:
            break
        out.append(j); j += 1
    return out

# config 1: 131766 nodes=[617771]
eid = 131766
print("== 131766 (config 1, node 617771) ==")
nid_pos = find_all(617771)
print(f"node 617771 u32 hits: {nid_pos[:10]}")
eid_pos = find_all(eid)
print(f"eid {eid} u32 hits: {eid_pos[:10]}")
# 找 node 位置与 eid 位置的距离
for np in nid_pos[:8]:
    near = [e for e in eid_pos if abs(e - np) < 300]
    print(f"  node@{np}: eid within 300 -> {near}")

# config 61: 589700 nodes=[753656, 758015]
print("\n== 589700 (config 61) ==")
for nid in (753656, 758015):
    np = find_all(nid)
    print(f"node {nid} u32 hits: {np[:8]}")
    near = [e for e in find_all(589700) if any(abs(e - n) < 300 for n in np)]
    print(f"  eid 589700 near node hits: {near}")

# config 22: 589100 nodes=[617751, 617756, 617752, 617757]
print("\n== 589100 (config 22) ==")
for nid in (617751, 617756):
    np = find_all(nid)
    print(f"node {nid} u32 hits: {np[:8]}")
    near = [e for e in find_all(589100) if any(abs(e - n) < 300 for n in np)]
    print(f"  eid 589100 near node hits: {near}")
