
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

def byte_dump(p, seg, label, nbytes=80):
    print(f"== {label} seg@{seg} mod4={seg%4}")
    print("  header:", [u32(p, seg+j*4) for j in range(6)])
    s = seg + 24
    for k in range(0, nbytes, 4):
        print(f"  +{k:3d}: {p[s+k:s+k+4].hex()} u32={u32(p,s+k):>10d} u16=({u16(p,s+k):>5d},{u16(p,s+k+2):>5d})")

p1 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\body_side.hm")
byte_dump(p1, 390741, "body_side", 84)
print("E1 nodes [162,167,166,161] search:", end=" ")
hits = [i for i in range(0, len(p1)-16) if all(u32(p1, i+j*4)==v for j, v in enumerate([162,167,166,161]))]
print(hits[:4])

p2 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\head_2.hm")
byte_dump(p2, 56946, "head_2", 64)
print("E1 nodes [800,798,793,794] search:", end=" ")
hits = [i for i in range(0, len(p2)-16) if all(u32(p2, i+j*4)==v for j, v in enumerate([800,798,793,794]))]
print(hits[:4])

p3 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\1d_elements.hm")
segs = [i for i in range(len(p3)-16) if u32(p3, i)==997]
print("\n1d_elements segs:", [(s, [u32(p3, s+j*4) for j in range(6)]) for s in segs])
byte_dump(p3, segs[0], "1d_elements", 48)
