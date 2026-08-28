"""v17 特殊元素深度 dump: config 1/21/22/61 + 未匹配 config 3/55 样本, 全 hit 宽窗口."""
import sys, struct, re
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, _collect_node_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
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

oracle = {}
for line in open("output/ground_truth/v17_missing_full.txt", encoding="utf-8", errors="replace"):
    line = line.strip()
    m = re.match(r"E eid=(\d+) config=(\d+) nodes=(.*)", line)
    if m:
        oracle[int(m.group(1))] = (int(m.group(2)), [int(x) for x in m.group(3).split()])

def hits_of(eid):
    pat = struct.pack("<I", eid)
    out = []
    j = 0
    while True:
        j = p.find(pat, j)
        if j < 0:
            break
        out.append(j); j += 1
    return out

targets = {
    131766: (1, [617771]),
    131767: (1, [623686]),
    589100: (22, [617751, 617756, 617752, 617757]),
    589101: (22, None),   # 用 oracle 里查
    589700: (61, [753656, 758015]),
    589705: (61, [753656, 756980]),
    131520: (3, None),    # 未匹配 config 3
    131633: (55, [2911530, 2911535, 2911536, 2911553]),
}

for eid in (131766, 131767, 589100, 589700, 589705, 589137, 589150):
    if eid in oracle:
        cfg, nds = oracle[eid]
        rows = [row_of.get(n) for n in nds]
        print(f"\n{'='*60}\neid={eid} config={cfg} nodes={nds} rows={rows}")
        for h in hits_of(eid)[:8]:
            # 找窗口内 oracle row 命中
            orowset = set(rows)
            u16m = [o for o in range(h + 4, min(h + 260, len(p) - 2), 2) if u16(p, o) in orowset]
            u32m = [o for o in range(h + 4, min(h + 260, len(p) - 4), 4) if (u32(p, o) >> 16) in orowset]
            print(f"  hit@{h}: u16rows@{u16m} u32hi@{u32m}")
            if u16m or u32m:
                print("   dump [0,120]:")
                for off in range(0, 120, 4):
                    q = h + off
                    if q + 4 > len(p):
                        break
                    v = u32(p, q)
                    mark = ""
                    if u16(p, q + 2) in orowset:
                        mark = f" <row{u16(p, q+2)}>"
                    if u16(p, q) in orowset:
                        mark = f" <row{u16(p, q)}>"
                    print(f"    +{off:3d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)}){mark}")
                break
