"""v17 family-1 全局扫描 (修正 row_map) + 输出剩余缺失元素清单."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, _collect_node_segments, parse_nodes

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
print(f"row_map rows={len(row_map)}")

f = open("output/ground_truth/v17gt_dummy_elemids.txt")
f.readline(); f.readline()
gt = set(int(l) for l in f if l.strip())
f.close()
print(f"gt elems={len(gt)}")

# family-1 全局扫描
MARK1 = struct.pack("<HH", 701, 2596)
MARK2 = struct.pack("<HH", 686, 2596)
cores = {}
for MARK, tag in ((MARK1, "701"), (MARK2, "686")):
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
            if 1 <= len(rows) <= 20 and all(1 <= r <= len(row_map) for r in rows):
                cores.setdefault(eid, (cfg - 256, tuple(rows)))
        j += 2
print(f"family-1 cores: {len(cores)}, in gt: {sum(1 for e in cores if e in gt)}")

missing = sorted(gt - set(cores))
print(f"missing: {len(missing)}")
runs = []
if missing:
    start = prev = missing[0]
    for v in missing[1:]:
        if v == prev + 1:
            prev = v
        else:
            runs.append((start, prev)); start = prev = v
    runs.append((start, prev))
print("runs:", runs)

# 保存缺失清单供后续逆向
with open("output/ground_truth/v17_missing_after_family1.txt", "w") as fo:
    for v in missing:
        fo.write(f"{v}\n")
