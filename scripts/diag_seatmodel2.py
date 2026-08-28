"""对比 SEAT_MODEL: family-1 检测启停的元素数."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments, _parse_a_type

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])
segs = find_elem_segments(p)

# 统计: 每段 family-1 检测命中数 vs 记录数
f1_eids = set()
tot = 0
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_a_type(p, sh, cnt, len(n1), row_map)
    if got:
        tot += len(got)
print(f"decoded (with family-1): {tot}")

# oracle
lines = open("output/ground_truth/SEAT_MODEL_elemids.txt").read().splitlines() if __import__('os').path.exists("output/ground_truth/SEAT_MODEL_elemids.txt") else []
gt = set(int(l) for l in lines[3:] if l.strip()) if lines else None
print("oracle eids:", len(gt) if gt else "N/A")
if gt:
    print("decoded in oracle:", len(set(range(0)) | (gt & _parse_all := set()))) if False else None
