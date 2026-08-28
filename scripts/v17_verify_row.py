"""验证 131694 的 oracle 行号与记录对比."""
import sys
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
print(f"rows={len(row_map)}")

for nid in (3462253, 3462254, 2000000, 3462316, 3462317, 617771, 623686):
    print(f"nid {nid} -> row {row_of.get(nid)}")

# 131694 真实记录: @37995033+106=36402, +158=116665, +162=116666
print("\n记录值: 36402, 116665, 116666")
print("oracle: [3462253, 3462254, 2000000]")
print("row_map[116665] =", row_map.get(116665), "row_map[116666] =", row_map.get(116666))
print("row_map[116664] =", row_map.get(116664))
