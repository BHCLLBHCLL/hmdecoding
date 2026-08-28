"""SEAT_MODEL: parse_nodes 细节 + row_map 正确性."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section, parse_nodes

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
print("ns:", ns)
hi, count, base, stride, idoff, chain = ns
n1, b1 = parse_nodes(p, ns)
print("parse_nodes len:", len(n1))
print("max nid in nodes:", max(n1) if n1 else None, "min:", min(n1) if n1 else None)

# 检查最后几条 node 记录的 nid 与坐标
for k in range(count - 3, count):
    rec = base + k * stride
    nid = u32(p, rec + 44) - 1
    x = d64(p, rec)
    print(f"  row {k+1}: nid={nid} x={x:.4f}")
