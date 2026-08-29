
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
ids = [u32(p, base + k*ns[3] + ns[4]) for k in range(ns[1])]
id2row = {nid: k+1 for k, nid in enumerate(ids)}
print("num ids:", len(ids), "max id:", max(ids) if ids else 0, "min:", min(ids) if ids else 0)
for nid in (1513, 1541, 1899, 1512, 1569, 1571):
    print(f"id {nid} -> row {id2row.get(nid)}")
# E1739 rows
r = [id2row.get(n) for n in (1513, 1541, 1899, 1512)]
print("E1739 rows:", r)
# search bad record @85357 for these rows (u16 pair [attr,row] or u32>>16)
h = 85357
for off in range(44, 70, 4):
    u16v = u32(p, h + off + 2) & 0xFFFF  # lower u16 (row) if [attr,row]
    print(f"  +{off}: u32={u32(p,h+off):>10d} hi={u32(p,h+off)>>16} lo16={u16v}")
