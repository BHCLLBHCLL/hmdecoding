
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\body_side_assembly.hm")
segs = find_elem_segments(p)
for sh, segid, cfg71, cnt, X, Y in segs:
    if segid == 48:
        print("seg48 @", sh, "header:", [u32(p, sh+j*4) for j in range(6)])
        s = sh + 24
        for k in range(0, 64, 4):
            print(f"  +{k:3d}: {p[s+k:s+k+4].hex()} u32={u32(p,s+k):>10d} u16=({u16(p,s+k):>5d},{u16(p,s+k+2):>5d})")
        # count 0x1a040be4 in seg48 range
        nxt = segs[[i for i,x in enumerate(segs) if x[1]==48][0]+1][0] if segs.index(segs[0]) < len(segs)-1 else len(p)
        # find next seg sh
        nxt = None
        for s2 in segs:
            if s2[0] > sh:
                nxt = s2[0]; break
        pat = b"\xe4\x0b\x04\x1a"
        n = 0; j = sh+24
        while j < (nxt or len(p)):
            j = p.find(pat, j, nxt or len(p))
            if j < 0: break
            n += 1; j += 1
        print("0x1a040be4 heads in seg48:", n, "next seg:", nxt)
