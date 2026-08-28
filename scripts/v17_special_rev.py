"""v17 特殊元素逆向: 对缺失样本, 找含 oracle 行号的真实记录并 dump."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, _collect_node_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")

# 修正 row_map
segs = _collect_node_segments(p)
row_map = {}
row = 0
for hi, cnt, base, stride, idoff, chain in segs:
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
    found = False
    for h in hits:
        # 窗口 [h+4, h+128] 内找 oracle rows (u32 或 u16)
        u32m = [o for o in range(h + 4, min(h + 128, len(p) - 4), 4) if u32(p, o) in orows]
        u16m = [o for o in range(h + 4, min(h + 128, len(p) - 2), 2) if u16(p, o) in orows]
        if u32m or u16m:
            print(f"  HIT @{h}: u32rows@{u32m} u16rows@{u16m}")
            if not found:
                for off in range(0, min(96, len(p) - h - 4), 4):
                    q = h + off
                    print(f"    +{off:3d}: {p[q:q+4].hex(' ')} u32={u32(p,q):<10d} u16=({u16(p,q)},{u16(p,q+2)})")
                found = True
    if not found:
        print("  no hit with oracle rows found; hits:", hits[:6])
