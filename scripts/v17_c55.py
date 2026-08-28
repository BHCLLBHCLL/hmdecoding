"""dump config 55 样本完整记录: 131633 (4节点) vs 131634 (6节点) vs NOMATCH 列表."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

p = open("output/ground_truth/v17_payload.bin", "rb").read()

def dump(h, lo, hi, label):
    print(f"\n== {label} @{h} ==")
    for off in range(lo, hi, 4):
        q = h + off
        if q + 4 > len(p):
            continue
        v = u32(p, q)
        print(f"  {off:+5d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)})")

dump(38019557, 0, 100, "131633 config55 (4n) oracle rows [41598,41603,41604,41621]")
dump(38019701, 0, 100, "131634 config55 (6n) oracle rows [48909,48912,48935,48936,48937,48938]")
