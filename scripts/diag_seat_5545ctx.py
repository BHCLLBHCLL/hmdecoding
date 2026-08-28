"""SEAT_MODEL: dump 2329950..2330100 查看 config 104 eid 5545 所在段."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, is_const

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
for off in range(2329950, 2330100, 2):
    q = off
    v = u16(p, q)
    mark = " <997>" if v == 997 else (" <CONST>" if is_const(u32(p, q)) else "")
    print(f"  {q}: {p[q:q+2].hex(' ')} u16={v}{mark}")
