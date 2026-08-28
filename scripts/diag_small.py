"""诊断极小型 v11 文件 decode 失败原因."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section, find_node_section_struct, parse_nodes

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\shell_section.hm")
print(f"payload: {len(p)} bytes")
print(f"header: {p[:64].hex(' ')}")
print(f"db_version: {d64(p, 4)}")

ns = find_node_section(p)
print(f"find_node_section: {ns}")

# 找所有 [136] 头
hits = []
j = 0
while True:
    i = p.find(b"\x88\x00\x00\x00", j)
    if i < 0:
        break
    hits.append((i, u32(p, i + 4)))
    j = i + 1
print(f"[136] header hits: {hits[:10]}")

# 结构扫描
st = find_node_section_struct(p, multi=True)
print(f"find_node_section_struct: {st}")

# 元素段
from decoder import find_elem_segments
segs = find_elem_segments(p)
print(f"elem segs: {segs}")
