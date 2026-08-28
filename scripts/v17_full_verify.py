"""v17 特殊元素全量验证: config 55 用新规则, 其他用 F1, 359 个全比 oracle."""
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
    """从 hit 位置提取节点行号."""
    if cfg == 55:
        # 节点数 = u16@+14 + 1; 节点1@+18, 其余@+30+4i
        nn = u16(p, h + 14) + 1
        rows = [u16(p, h + 18)]
        rows += [u16(p, h + 30 + 4 * i) for i in range(nn - 1)]
        return rows
    # F1: (u16@+16+4i << 16) | u16@+14+4i
    return [(u16(p, h + 16 + 4 * i) << 16) | u16(p, h + 14 + 4 * i) for i in range(n_nodes)]

ok = 0
bad = []
for eid, (cfg, nds) in sorted(oracle.items()):
    rows_exp = [row_of.get(n) for n in nds]
    hits = hits_of(eid)
    best = None
    for h in hits:
        got = extract(h, cfg, len(nds))
        score = sum(1 for r in got if r in set(rows_exp))
        if best is None or score > best[0]:
            best = (score, h, got)
    if best and best[0] == len(rows_exp) and sorted(best[2]) == sorted(rows_exp):
        ok += 1
    else:
        bad.append((eid, cfg, len(nds), best, rows_exp))

print(f"exact match: {ok}/{len(oracle)}")
print(f"bad: {len(bad)}")
for eid, cfg, nn, best, rows_exp in bad:
    print(f"  eid={eid} cfg={cfg} n={nn} hit={best[1] if best else None} got={best[2] if best else None} exp={rows_exp}")
