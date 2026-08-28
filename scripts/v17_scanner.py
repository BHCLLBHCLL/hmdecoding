"""测试: 扫描 [eid][0][k=2|3][tag] 模式提取特殊元素, 与 oracle 对比."""
import sys, struct, re
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, _collect_node_segments, find_elem_segments

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
row_count = len(row_map)

oracle = {}
for line in open("output/ground_truth/v17_missing_full.txt", encoding="utf-8", errors="replace"):
    m = re.match(r"E eid=(\d+) config=(\d+) nodes=(.*)", line.strip())
    if m:
        oracle[int(m.group(1))] = (int(m.group(2)), [int(x) for x in m.group(3).split()])

SPECIAL_TAGS = {257: 1, 259: 3, 317: 61, 534: 22, 567: 55}

# 扫描: ZERO4 @j, eid = u32(j-4), k = u32(j+4), tag = u16(j+8)
ZERO4 = b"\x00\x00\x00\x00"
elems = {}
hits_pos = {}
start = 0
scan_from = 29_000_000  # 跳过节点段
while True:
    j = p.find(ZERO4, start)
    if j < 0:
        break
    eid = u32(p, j - 4) if j >= 4 else 0
    if 1 <= eid <= 10_000_000:
        k = u32(p, j + 4)
        if k in (2, 3):
            tag = u16(p, j + 8)
            cfg = SPECIAL_TAGS.get(tag)
            if cfg is not None:
                h = j - 4
                if h < scan_from:
                    start = j + 1
                    continue
                # 提取
                if cfg == 55:
                    n = u16(p, h + 14)
                    if not (0 <= n <= 40):
                        start = j + 1
                        continue
                    rows = []
                    rows.append(((u32(p, h + 20) & 0xFFFF) << 16) | (u32(p, h + 16) >> 16))
                    ok = rows[0] > 0
                    for i in range(1, n + 1):
                        low = u32(p, h + 28 + 4 * (i - 1)) >> 16
                        high = u32(p, h + 32 + 4 * (i - 1)) & 0xFFFF
                        r = (high << 16) | low
                        rows.append(r)
                    ok = ok and all(1 <= r <= row_count for r in rows)
                else:
                    rows = []
                    i = 0
                    ok = True
                    while True:
                        lo = u16(p, h + 14 + 4 * i)
                        if lo == 0 or len(rows) > 100:
                            break
                        hi = u16(p, h + 16 + 4 * i)
                        r = (hi << 16) | lo
                        rows.append(r)
                        i += 1
                    ok = len(rows) > 0 and all(1 <= r <= row_count for r in rows)
                if ok:
                    if eid not in elems:
                        elems[eid] = (cfg, list(rows))
                        hits_pos[eid] = h
    start = j + 1

print(f"scanned special elems: {len(elems)}")
print(f"in oracle: {sum(1 for e in elems if e in oracle)}")
oracle_ids = set(oracle)
missed = oracle_ids - set(elems)
extra = set(elems) - oracle_ids
print(f"missed: {len(missed)} -> {sorted(missed)[:20]}")
print(f"extra: {len(extra)} -> {sorted(extra)[:20]}")

# 验证节点
match = 0
for eid in oracle_ids & set(elems):
    cfg, rows = elems[eid]
    nds = [row_map.get(r) for r in rows]
    ocfg, onds = oracle[eid]
    if sorted(nds) == sorted(onds):
        match += 1
print(f"node match: {match}/{len(oracle_ids & set(elems))}")
