"""SEAT_MODEL: 构建真实 row_map (row->nid) 并核对缺失元素节点."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
hi, count, base, stride, idoff, chain = ns
print("ns:", ns)

# 构建 row_map: row (1-indexed) -> nid
row_map = {}
for k in range(count):
    rec = base + k * stride
    nid = u32(p, rec + 44) - 1 if chain else u32(p, rec + idoff)
    row_map[k + 1] = nid

# 核对关键 row
for r in (528, 529, 17370, 17371, 17373, 17374, 34296, 34328):
    print(f"row_map[{r}] = {row_map.get(r)}")

# 反向: 哪些 row 映射到 34328, 17373, 17374, 34327
targets = [34328, 17373, 17374, 34327, 528, 529]
inv = {}
for r, n in row_map.items():
    inv.setdefault(n, []).append(r)
for t in targets:
    print(f"nid {t} -> rows {inv.get(t)}")
