
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, is_const, find_elem_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\car_section.hm")
segs = find_elem_segments(p)
for sh, segid, cfg71, cnt, X, Y in segs:
    if segid == 154:
        # find CONST after sh+24
        consts = []
        j = sh + 24
        while True:
            j = p.find(b"\xf5\x1f", j, sh + 20000)
            if j < 0: break
            if is_const(u32(p, j)):
                consts.append(j)
            j += 1
        print("consts:", consts[:6], "spacing:", [consts[i+1]-consts[i] for i in range(min(5,len(consts)-1))])
        c0 = consts[0]
        for k in range(0, 140, 4):
            print(f"  rel{c0+k-c0:+4d}: {p[c0+k:c0+k+4].hex()} u32={u32(p,c0+k):>10d}")
