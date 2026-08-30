
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\abaqus_contactManager_2D_tutorial.hm")
segs = find_elem_segments(p)
for sh, segid, cfg71, cnt, X, Y in segs:
    print(f"seg{segid} @ {sh} cnt={cnt} Y={Y} header={[u32(p, sh+j*4) for j in range(6)]}")
    s = sh + 24
    for k in range(0, 44, 4):
        print(f"   +{k:2d}: {p[s+k:s+k+4].hex()} u32={u32(p,s+k):>9d}")
