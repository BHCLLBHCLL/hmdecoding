"""v17 逆向: 用已知 oracle 样本 (config+nodes) 定位缺失元素真实记录, 推断格式."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section_struct

p = open("output/ground_truth/v17_payload.bin", "rb").read()

# ---- 修正版 row_map: 去掉重叠过扫 + 加入小段 3 节点 ----
segs = sorted(find_node_section_struct(p, multi=True), key=lambda s: s[2])
print("detected segs:", [(s[2], s[1], s[3]) for s in segs])

fixed = []
for i, (hi, cnt, base, stride, idoff, chain) in enumerate(segs):
    end = base + cnt * stride
    nxt = None
    for j in range(i + 1, len(segs)):
        if segs[j][2] > base:
            nxt = segs[j][2]
            break
    if nxt is not None and end > nxt:
        cnt = (nxt - base) // stride
    fixed.append((None, cnt, base, stride, idoff, chain))
print("fixed segs:", [(s[2], s[1], s[3]) for s in fixed])

row_map = {}
row = 0
for hi, cnt, base, stride, idoff, chain in fixed:
    for k in range(cnt):
        rec = base + k * stride
        if rec + stride > len(p):
            break
        nid = u32(p, rec)
        x = d64(p, rec + 12)
        if not (1 <= nid <= 10_000_000) or not (abs(x) < 1e9):
            break
        row += 1
        row_map[row] = nid
print(f"fixed row_map rows: {len(row_map)} (need 354174)")

SMALL_BASE = 29980135
for k in range(3):
    rec = SMALL_BASE + k * 68
    nid = u32(p, rec)
    x = d64(p, rec + 12)
    if 1 <= nid <= 10_000_000 and abs(x) < 1e9:
        row += 1
        row_map[row] = nid
print(f"after small seg: {len(row_map)} (need 354176)")
row_of = {v: k for k, v in row_map.items()}

oracle = {
    131508: (3, [2991373, 2980505]),
    131633: (55, [2911530, 2911535, 2911536, 2911553]),
    131684: (60, [2996947, 2996948, 2000000]),
    131694: (60, [3462253, 3462254, 2000000]),
    131757: (60, [3462316, 3462317, 2000000]),
    131766: (1, [617771]),
    131767: (1, [623686]),
    589001: (3, [717301, 741336]),
    589100: (22, [617751, 617756, 617752, 617757]),
    589136: (55, [758618, 702778, 702774, 702768, 702770]),
    589137: (60, [113187, 113188]),
    589150: (60, [200031, 225912]),
    589700: (61, [753656, 758015]),
    589705: (61, [753656, 756980]),
    263827: (204, [219546, 220347, 220624, 219550]),
    263836: (204, [220624, 222533, 212332, 212411]),
    144230: (104, [433859, 433860, 433857, 433856]),
}

def find_all_u32(val):
    pat = struct.pack("<I", val)
    pos = []
    j = 0
    while True:
        j = p.find(pat, j)
        if j < 0:
            break
        pos.append(j); j += 1
    return pos

for eid, (cfg, nodes) in sorted(oracle.items()):
    orows = sorted(row_of.get(n) for n in nodes)
    print(f"\n=== eid={eid} config={cfg} oracle_rows={orows}")
    hits = find_all_u32(eid)
    shown = 0
    for h in hits:
        u32_m = [o for o in range(h + 8, min(h + 120, len(p) - 4), 4) if u32(p, o) in orows]
        u16_m = [o for o in range(h + 8, min(h + 120, len(p) - 2), 2) if u16(p, o) in orows]
        if u32_m or len(u16_m) >= 1:
            print(f"  hit@{h}: u32rows@{u32_m} u16rows@{u16_m}")
            if shown < 1 and (u32_m or len(u16_m) >= 2):
                for off in range(0, min(96, len(p) - h - 4), 4):
                    q = h + off
                    print(f"    +{off:3d}: {p[q:q+4].hex(' ')} u32={u32(p,q):<11d} u16=({u16(p,q)},{u16(p,q+2)})")
                shown += 1
