"""dump 131668 (config55 14n) 和 589125 (config55 5n) 完整记录, 找行号高16位."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

p = open("output/ground_truth/v17_payload.bin", "rb").read()

def dump(h, lo, hi, label):
    print(f"\n== {label} @{h} ==")
    for off in range(lo, hi, 4):
        q = h + off
        if q + 4 > len(p):
            break
        v = u32(p, q)
        print(f"  {off:+5d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)})")

dump(38025325, 0, 120, "131668 config55 n=14, exp [43329..43400, 116724, 116725]")
dump(65234043, 0, 80, "589125 config55 n=5, exp [277459, 278136, 278317, 277624, 277737]")
