
import sys, os, struct
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_elem_segments

for fname, sub in [("wing_section_complete.hm", ""), ("hm-ansys_contact_wizard_2-d_tutorial.hm", "interfaces/ansys/")]:
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{sub}{fname}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/{fname}"
    p = load_payload(path)
    print(f"== {fname}: db={d64(p,4)} len={len(p)}")
    segs = find_elem_segments(p)
    from collections import Counter
    print("  Y dist:", dict(Counter(s[4] for s in segs)))
    print("  segs:", [(s[1], s[3], s[4], s[5]) for s in segs[:6]])
    if segs:
        sh, segid, cfg71, cnt, X, Y = segs[0]
        s = sh + 24
        print("  seg0 @", sh, "header:", [u32(p, sh+j*4) for j in range(6)])
        for k in range(0, 48, 4):
            print(f"    +{k:3d}: {p[s+k:s+k+4].hex()} u32={u32(p,s+k):>9d}")
