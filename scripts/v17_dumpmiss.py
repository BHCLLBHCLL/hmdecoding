"""dump 漏掉的特殊元素: 131766(config1), 589074(config22), 131678(config55)."""
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

dump(65219741, 0, 64, "131766 config1 @65219741 (1 node 250984)")
dump(65219889, 0, 48, "589074 config22 @65219889 (2 nodes)")
dump(65222687, 0, 40, "589100 config22 @65222687 (4 nodes)")
dump(38027317, 0, 80, "131678 config55 @38027317 (56 nodes)")
