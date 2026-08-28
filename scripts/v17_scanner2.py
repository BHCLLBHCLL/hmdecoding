"""v17 特殊元素扫描器 v2: 完整 tag 映射, n 上限 100, config 1 固定 1 节点."""
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
row_count = len(row_map)

oracle = {}
for line in open("output/ground_truth/v17_missing_full.txt", encoding="utf-8", errors="replace"):
    m = re.match(r"E eid=(\d+) config=(\d+) nodes=(.*)", line.strip())
    if m:
        oracle[int(m.group(1))] = (int(m.group(2)), [int(x) for x in m.group(3).split()])

SPECIAL_TAGS = {257: 1, 259: 3, 277: 21, 278: 22, 534: 22, 790: 22, 1558: 22, 567: 55, 317: 61}

ZERO4 = b"\x00\x00\x00\x00"
elems = {}
start = 0
scan_from = 29_000_000
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
                if h >= scan_from:
                    rows = []
                    ok = True
                    if cfg == 55:
                        n = u16(p, h + 14)
                        if 0 <= n <= 100:
                            rows.append(((u32(p, h + 20) & 0xFFFF) << 16) | (u32(p, h + 16) >> 16))
                            for i in range(1, n + 1):
                                low = u32(p, h + 28 + 4 * (i - 1)) >> 16
                                high = u32(p, h + 32 + 4 * (i - 1)) & 0xFFFF
                                rows.append((high << 16) | low)
                        else:
                            ok = False
                        ok = ok and all(1 <= r <= row_count for r in rows)
                    else:
                        if cfg == 1:
                            # config 1: 单节点
                            lo = u16(p, h + 14)
                            hi = u16(p, h + 16)
                            rows = [(hi << 16) | lo]
                        else:
                            i = 0
                            while len(rows) <= 100:
                                lo = u16(p, h + 14 + 4 * i)
                                if lo == 0:
                                    break
                                hi = u16(p, h + 16 + 4 * i)
                                rows.append((hi << 16) | lo)
                                i += 1
                        ok = len(rows) > 0 and all(1 <= r <= row_count for r in rows)
                    if ok and eid not in elems:
                        elems[eid] = (cfg, list(rows))
    start = j + 1

print(f"scanned special elems: {len(elems)}")
oracle_ids = set(oracle)
missed = oracle_ids - set(elems)
extra = set(elems) - oracle_ids
print(f"missed: {len(missed)} -> {sorted(missed)[:25]}")
print(f"extra: {len(extra)} -> {sorted(extra)[:15]}")

match = 0
for eid in oracle_ids & set(elems):
    cfg, rows = elems[eid]
    nds = [row_map.get(r) for r in rows]
    ocfg, onds = oracle[eid]
    if sorted(nds) == sorted(onds):
        match += 1
print(f"node match: {match}/{len(oracle_ids & set(elems))}")
