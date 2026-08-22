
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\body_side.hm")
hdr = 390741
print("body_side elem hdr@390741: [997,1,175,7182,3,4]")
for off in range(0, 160, 16):
    b = p[hdr+off : hdr+off+16]
    u = [u32(p, hdr+off+j) for j in range(0,16,4)]
    print(f"  +{off:4d}: {u}  raw={b.hex()}")

p2 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\1d_elements.hm")
print()
print("1d_elements: find 997 headers")
hits = [i for i in range(len(p2)-16) if u32(p2,i)==997]
print(" hits:", [(h, [u32(p2,h+4*j) for j in range(8)]) for h in hits[:8]])
