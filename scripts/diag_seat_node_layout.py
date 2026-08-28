"""SEAT_MODEL: dump 节点段头部原始字节, 确认 56B vs 96B 布局."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
hi, count, base, stride, idoff, chain = ns
print("ns:", ns)

# dump 前 2 条记录 (base 附近)
for k in range(2):
    rec = base + k * 56
    print(f"\n== node record {k} (rec={rec}) ==")
    for off in range(0, 56, 4):
        q = rec + off
        print(f"  +{off:2d}: {p[q:q+4].hex(' ')} u32={u32(p,q):<12d} u16=({u16(p,q)},{u16(p,q+2)}) d64={d64(p,q):.4f}")

# 检查是否有 0x10200bc7 标记 (v13.03 96B)
print("\n== 搜索 0x10200bc7 标记 ==")
mark = (0x10200bc7).to_bytes(4, "little")
cnt = 0
j = 0
while True:
    j = p.find(mark, j)
    if j < 0:
        break
    if cnt < 5:
        print(f"  mark @ {j}")
    cnt += 1
    j += 1
print("  total marks:", cnt)
