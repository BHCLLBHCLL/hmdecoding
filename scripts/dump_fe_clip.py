
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\fe_only.hm")
seg = 4748145
print(f"fe_only seg@{seg}: header={[u32(p,seg+j*4) for j in range(6)]}")
s = seg + 24
print(f"record stream from {s}, first record 98B (n=8):")
for k in range(0, 98, 4):
    print(f"  {k:+4d}: {p[s+k:s+k+4].hex()} u32={u32(p,s+k)} u16=({u16(p,s+k)},{u16(p,s+k+2)})")
print("E191098 nodes @4748179:", [u32(p, 4748179+j*4) for j in range(8)])
print("rel node area:", 4748179 - s)

p2 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\clip_refine.hm")
seg2 = 972751
print(f"\nclip_refine seg@{seg2}: header={[u32(p2,seg2+j*4) for j in range(6)]}")
s2 = seg2 + 24
print(f"record stream from {s2}:")
for k in range(0, 56, 4):
    print(f"  {k:+4d}: {p2[s2+k:s2+k+4].hex()} u32={u32(p2,s2+k)} u16=({u16(p2,s2+k)},{u16(p2,s2+k+2)})")
print("E1 nodes @972799:", [u32(p2, 972799+j*4) for j in range(4)])
print("rel node area:", 972799 - s2)
