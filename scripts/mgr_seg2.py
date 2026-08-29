
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
segs = find_elem_segments(p)
sh1 = segs[0][0]; sh2 = segs[1][0]
pat = b"\x1f\x0b\x20\x30"
# heads per seg
h1 = [i for i in range(0, len(p)-4) if p[i:i+4] == pat and sh1 <= i < sh2]
h2 = [i for i in range(0, len(p)-4) if p[i:i+4] == pat and i >= sh2]
print("heads seg1:", len(h1), "seg2:", len(h2))
print("seg1 span:", sh1, sh2)
# seg1 first head dump
print("--- seg1 head ---")
h = h1[0]
for k in range(0, 48, 4):
    print(f"  +{k:3d}: {p[h+k:h+k+4].hex()} u32={u32(p,h+k):>10d}")
# seg2 non-head area: dump after last head in seg2
print("--- seg2 dump around first few NON-head records ---")
# find region after seg1's last head and before seg2 first head
print("seg1 head0..3:", h1[:3], "seg2 head0..3:", h2[:3])
print("seg2 area starts", sh2)
for k in range(0, 80, 4):
    o = sh2 + 24 + k
    print(f"  {sh2+24+k-sh2-24:+4d}: {p[o:o+4].hex()} u32={u32(p,o):>10d}")
