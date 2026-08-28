"""SEAT_MODEL: 定位节点 34328 与 17374, 确认节点段真实边界."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
hi, count, base, stride, idoff, chain = ns
print("ns:", ns)
print("node section end (base+count*stride):", base + count * stride)

# 搜索 nid+1 = 34329 (0x8619) 和 17375 (0x43DF 表示 nid 17374+1) 与 17376
import struct
def find_u32(v):
    b = struct.pack("<I", v)
    hits = []
    j = 0
    while True:
        j = p.find(b, j)
        if j < 0:
            break
        hits.append(j)
        j += 1
    return hits

for label, v in [("nid+1=34329", 34329), ("nid+1=17375(17374)", 17375), ("nid+1=17376(17375)", 17376), ("nid+1=34328(34327)", 34328)]:
    hits = find_u32(v)
    # 过滤到节点段附近 (100000..2040000)
    nearby = [h for h in hits if 100000 <= h <= 2040000]
    print(f"{label}: total {len(hits)} hits, node-region {len(nearby)}: {nearby[:10]}")

# dump 节点段末尾 到 seg0 之间
print("\n== dump 2030800..2030900 ==")
for off in range(2030800, 2030900, 4):
    q = off
    print(f"  {q}: {p[q:q+4].hex(' ')} u32={u32(p,q)}")
