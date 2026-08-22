
import sys, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments

for fname in ["c_channel-tcl.hm", "composites.hm", "crash_tubes.hm", "joints.hm", "chapter2_1.hm",
              "body_side_assembly.hm", "abaqus3_0tutorial.hm", "geometry.hm", "rear_truss_1_new.hm", "pene_dyna.hm"]:
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{fname}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/interfaces/ansys/{fname}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/{fname}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/interfaces/abaqus/{fname}"
    p = load_payload(path)
    segs = find_elem_segments(p)
    print(f"== {fname}: segs={[(s[1], s[3], s[4], s[5]) for s in segs[:6]]} total={len(segs)}")
    if segs:
        sh, segid, cfg71, cnt, X, Y = segs[0]
        print("   head bytes:", [u32(p, sh+j*4) for j in range(6)])
