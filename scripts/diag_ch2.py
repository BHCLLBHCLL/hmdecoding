"""诊断 chapter2_2.hm (v13.03) 节点/元素布局."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section, find_node_section_struct, find_elem_segments, _collect_node_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\chapter2_2.hm")
print(f"payload {len(p)} db={d64(p,4)}")
print(f"header: {p[:48].hex(' ')}")

ns = find_node_section(p)
print("find_node_section:", ns)
st = find_node_section_struct(p, multi=True)
print("struct:", [(s[2], s[1], s[3]) for s in st])
segs = find_elem_segments(p)
print("elem segs:", segs[:5])
# 零4 定位节点候选 (52/56/68/92)
hits = []
j = 0
while j < len(p):
    j = p.find(b"\x00\x00\x00\x00", j)
    if j < 0:
        break
    base = j - 4
    if base >= 0:
        nid = u32(p, base)
        if 1 <= nid <= 10000000:
            hits.append(base)
    j += 1
print(f"zero4 nid candidates: {len(hits)} first 20: {hits[:20]}")
