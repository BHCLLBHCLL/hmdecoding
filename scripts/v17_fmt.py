"""v17 特殊记录格式自动验证: 对每个缺失 eid, 测试候选格式, 统计匹配."""
import sys, struct, re
from collections import defaultdict, Counter
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

def try_format(h, rows_set, n_nodes):
    """返回 (匹配数, 节点行号列表, 格式名)."""
    results = []
    # F1: 每节点 (high u16 @+16+4i, low u16 @+14+4i)
    try:
        got = [(u16(p, h + 16 + 4 * i) << 16) | u16(p, h + 14 + 4 * i) for i in range(n_nodes)]
        results.append((sum(1 for r in got if r in rows_set), got, "F1_hi@16_lo@14"))
    except Exception:
        pass
    # F2: node = (u32@+8 << 16) | u16@+14 (单节点)
    try:
        got = [((u32(p, h + 8) if u32(p, h + 8) < 0x10000 else 0) << 16) | u16(p, h + 14)]
        results.append((sum(1 for r in got if r in rows_set), got, "F2"))
    except Exception:
        pass
    # F3: 节点 = u32 @ +14+4i
    try:
        got = [u32(p, h + 14 + 4 * i) for i in range(n_nodes)]
        results.append((sum(1 for r in got if r in rows_set), got, "F3_u32@14"))
    except Exception:
        pass
    # F4: 节点 = u16 @ +14+4i (仅低16位, 匹配 lo16)
    lo16 = {r & 0xFFFF for r in rows_set}
    try:
        got = [u16(p, h + 14 + 4 * i) for i in range(n_nodes)]
        results.append((sum(1 for r in got if r in lo16), got, "F4_u16@14_lo16"))
    except Exception:
        pass
    # F5: 节点 = u32@+12+4i 的高16位 (row<<16|flag)
    try:
        got = [u32(p, h + 12 + 4 * i) >> 16 for i in range(n_nodes)]
        results.append((sum(1 for r in got if r in rows_set), got, "F5_hi@12"))
    except Exception:
        pass
    # F6: 节点 = u32@+8+4i 的高16位
    try:
        got = [u32(p, h + 8 + 4 * i) >> 16 for i in range(n_nodes)]
        results.append((sum(1 for r in got if r in rows_set), got, "F6_hi@8"))
    except Exception:
        pass
    return max(results, key=lambda x: x[0]) if results else (0, [], "none")

# 统计每种 config 的最佳格式
best_by_cfg = defaultdict(list)
total = 0
ok = 0
for eid, (cfg, nds) in sorted(oracle.items()):
    rows = [row_of.get(n) for n in nds]
    rows_set = set(rows)
    hits = hits_of(eid)
    best = (0, [], "none", None)
    for h in hits:
        score, got, fname = try_format(h, rows_set, len(nds))
        if score > best[0]:
            best = (score, got, fname, h)
    total += 1
    if best[0] >= len(nds) * 0.5:
        ok += 1
        best_by_cfg[cfg].append((eid, best[2], best[3], best[1], rows))
    else:
        best_by_cfg[cfg].append((eid, "NOMATCH", best[3], best[1], rows))

print(f"matched (>=50%): {ok}/{total}")
for cfg in sorted(best_by_cfg):
    es = best_by_cfg[cfg]
    fmt_cnt = Counter(x[1] for x in es)
    print(f"\nconfig {cfg} (n={len(es)}): format dist {dict(fmt_cnt)}")
    for eid, fname, h, got, rows in es[:5]:
        print(f"  eid={eid} fmt={fname} hit={h} got={got} oracle={rows}")
