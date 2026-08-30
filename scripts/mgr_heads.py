
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
segs = find_elem_segments(p)
sh2 = segs[1][0]
pat = b"\x1f\x0b\x20\x30"
h2 = []
j = sh2
while True:
    j = p.find(pat, j, sh2 + 40000)
    if j < 0: break
    h2.append(j)
    j += 62
print("seg2 heads:", len(h2), "first:", h2[:3], "eids:", [u32(p, j+24) for j in h2[:5]])
# sample: what eid do the 28 heads cover
print("head eids:", [u32(p, j+24) for j in h2])
# non-head area between heads h2[k] and h2[k+1] (should be 62B apart)
print("head spacing:", [h2[i+1]-h2[i] for i in range(min(6, len(h2)-1))])
# look for CONST or other mark between heads
# dump around h2[0] + 62 (where next record would be if no head)
print("--- after first seg2 head @", h2[0], "---")
base = h2[0]
for k in range(62, 200, 4):
    print(f"  +{k:3d}: {p[base+k:base+k+4].hex()} u32={u32(p,base+k):>10d}")
