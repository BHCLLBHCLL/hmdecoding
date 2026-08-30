
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
segs = find_elem_segments(p)
sh2 = segs[1][0]
nxt = len(p) if len(segs) < 3 else segs[2][0]
print("seg2 @", sh2, "next:", nxt, "span:", nxt - sh2)
pat = b"\x1f\x0b\x20\x30"
# find non-head gaps: records between heads
heads = []
j = sh2
while True:
    j = p.find(pat, j, nxt)
    if j < 0: break
    heads.append(j)
    j += 1
print("heads:", len(heads), "positions:", heads)
# dump region between head 45 (heads[0]) and head 150 (heads[1]) - is it 62B?
if len(heads) > 1:
    gap = heads[1] - (heads[0] + 62)
    print("gap between first two heads:", gap)
# dump after last head to segment end
print("last head:", heads[-1], "to next:", nxt - heads[-1])
# dump a window in the middle (where non-head records might be)
h = heads[0]
print("--- around first head @", h, "---")
for k in range(-120, 120, 4):
    o = h + k
    if sh2 <= o < nxt:
        print(f"  {k:+5d}: {p[o:o+4].hex()} u32={u32(p,o):>10d}")
