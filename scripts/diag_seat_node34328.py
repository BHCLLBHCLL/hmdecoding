"""SEAT_MODEL: 精查节点段末尾, 定位节点 34328 的 nid 存储位置."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
hi, count, base, stride, idoff, chain = ns
print("ns:", ns)

# 节点 34327 记录 (k=34294) 与 34328 记录 (k=34295)
for k in (34294, 34295):
    rec = base + k * stride
    print(f"\n== record k={k} rec={rec} (row {k+1}) ==")
    print(f"  x=d64({rec})={d64(p,rec):.6f}")
    print(f"  y=d64({rec+8})={d64(p,rec+8):.6f}")
    print(f"  z=d64({rec+16})={d64(p,rec+16):.6f}")
    for off in range(24, 56, 4):
        print(f"  +{off}: u32={u32(p,rec+off)}  u16=({u16(p,rec+off)},{u16(p,rec+off+2)})")

# 节点段之后 44 字节 (2030813..2030857) 逐字节
print("\n== 2030813..2030860 逐字节 ==")
for off in range(2030813, 2030861):
    print(f"  {off}: {p[off]:02x}")
