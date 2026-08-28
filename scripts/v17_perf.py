"""family-1 全局扫描性能测试."""
import sys, time, struct
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, _collect_node_segments, parse_nodes

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
segs = _collect_node_segments(p)
nodes = {}
for s in segs:
    n, _ = parse_nodes(p, s)
    nodes.update(n)
row_map = {}
row = 0
for hi, cnt, base, stride, idoff, chain in sorted(segs, key=lambda s: s[2]):
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
row_count = len(nodes)

t0 = time.time()
MARK1 = struct.pack("<HH", 701, 2596)
MARK2 = struct.pack("<HH", 686, 2596)
elems = {}
for MARK in (MARK1, MARK2):
    j = 0
    while True:
        j = p.find(MARK, j)
        if j < 0:
            break
        q = j
        eid = u16(p, q + 8) | (u16(p, q + 10) << 16)
        flag = u32(p, q + 18)
        cfg = flag >> 16
        if 300 <= cfg <= 500 and (flag & 0xFFFF) == 0 and 1 <= eid <= 10_000_000:
            rows = []
            k = q + 22
            while u32(p, k) != 0 and len(rows) < 20:
                rows.append(u32(p, k)); k += 4
            if 1 <= len(rows) <= 20 and all(1 <= r <= row_count for r in rows):
                elems.setdefault(eid, (cfg - 256, tuple(rows)))
        j += 2
print(f"family-1 cores: {len(elems)} t={time.time()-t0:.1f}s")

t0 = time.time()
spec_from = max(s[2] + s[1] * s[3] for s in segs)
from decoder import _parse_special_elems
spec = _parse_special_elems(p, row_map, row_count, scan_from=spec_from)
print(f"special: {len(spec)} t={time.time()-t0:.1f}s")
elems.update(spec)
print(f"total: {len(elems)}")

# 与 oracle 对比
f = open("output/ground_truth/v17gt_dummy_elemids.txt")
f.readline(); f.readline()
gt = set(int(l) for l in f if l.strip())
f.close()
print(f"gt={len(gt)} missing={len(gt - set(elems))} extra={len(set(elems) - gt)}")
