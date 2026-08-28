"""truck Y=7/Y=4 段: 完整记录 dump (28 词)."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, is_const

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
segs = find_elem_segments(p)

def dump_full(sh, segid, cnt, X, Y, nrec=3):
    print(f"\n===== seg {segid} Y={Y} cnt={cnt} =====")
    anchors = []
    j = sh + 16
    end = min(sh + 200000, len(p))
    while j < end:
        if is_const(u32(p, j)):
            anchors.append(j)
        j += 4
    for i in range(min(nrec, len(anchors))):
        a = anchors[i]
        b = anchors[i+1] if i+1 < len(anchors) else a + 200
        words = [u32(p, a + 4*k) for k in range((b-a)//4)]
        print(f"  rec{i} @{a} len={b-a}:")
        print(f"    {words}")

for sh, segid, cfg71, cnt, X, Y in segs:
    if (Y == 7 and cnt > 100) or (Y == 4 and cnt > 100):
        dump_full(sh, segid, cnt, X, Y, nrec=2)
