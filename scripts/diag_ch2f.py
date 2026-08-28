"""dump chapter2_2 seg2 连续 6 条记录 (eid 3-8)."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, is_const

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\chapter2_2.hm")
sh = 391328
rec = sh + 52  # 第一条记录 (CONST@+48 后)
for k in range(6):
    print(f"\n== rec{k} @{rec} ==")
    for off in range(0, 76, 4):
        q = rec + off
        v = u32(p, q)
        print(f"  +{off:2d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)})")
    rec += 76
