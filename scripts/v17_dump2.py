"""dump 131766 @65219741 和 node 617771 @65254167 的上下文."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

p = open("output/ground_truth/v17_payload.bin", "rb").read()

def dump(h, lo, hi, label):
    print(f"\n== {label} @{h} ==")
    for off in range(lo, hi, 4):
        q = h + off
        if q < 0 or q + 4 > len(p):
            continue
        v = u32(p, q)
        print(f"  {off:+5d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)})")

dump(65219741, -32, 96, "eid 131766 @65219741")
dump(65254167, -16, 80, "node 617771 @65254167")
dump(65255117, -16, 80, "node 617771 @65255117")
