"""v17 特殊元素最终验证: config55 用 next-u32-low16 规则, 其他用 F1."""
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
    m = re.match(r"E eid=(\d+) config=(\d+) nodes=(.*)", line.strip())
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

def extract(h, cfg, n_nodes):
    if cfg == 55:
        n = u16(p, h + 14)
        rows = []
        rows.append(((u32(p, h + 20) & 0xFFFF) << 16) | (u32(p, h + 16) >> 16))
        for i in range(1, n + 1):
            low = u32(p, h + 28 + 4 * (i - 1)) >> 16
            high = u32(p, h + 32 + 4 * (i - 1)) & 0xFFFF
            rows.append((high << 16) | low)
        return rows
    return [(u16(p, h + 16 + 4 * i) << 16) | u16(p, h + 14 + 4 * i) for i in range(n_nodes)]

ok = 0
bad = []
for eid, (cfg, nds) in sorted(oracle.items()):
    rows_exp = [row_of.get(n) for n in nds]
    hits = hits_of(eid)
    best = None
    for h in hits:
        got = extract(h, cfg, len(nds))
        if sorted(got) == sorted(rows_exp):
            best = (h, got)
            break
        # 部分匹配分
        score = sum(1 for r in got if r in set(rows_exp))
        if best is None or score > best[0]:
            best = (h, got)
    if best and sorted(best[1]) == sorted(rows_exp):
        ok += 1
    else:
        bad.append((eid, cfg, len(nds), best, rows_exp))

print(f"exact match: {ok}/{len(oracle)}")
for eid, cfg, nn, best, rows_exp in bad:
    print(f"  eid={eid} cfg={cfg} n={nn} hit={best[0] if best else None} got={sorted(best[1]) if best else None} exp={rows_exp}")
