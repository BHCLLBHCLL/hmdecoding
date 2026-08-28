"""dump chapter2_2 节点候选区 111390-111600."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\chapter2_2.hm")
for off in range(111390, 111620, 8):
    q = off
    v = u32(p, q)
    d = d64(p, q)
    print(f"{q}: {p[q:q+8].hex(' ')} u32={v:<10d} d={d:.5g} u16=({u16(p,q)},{u16(p,q+2)})")
