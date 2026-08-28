"""car_section: segid 202 的 CONST 锚点与 stride."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, is_const

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/car_section.hm")
segs = find_elem_segments(p)
for sh, segid, cfg71, cnt, X, Y in segs:
    if segid == 202:
        # 找所有 CONST 锚点 (前 8 个)
        consts = []
        j = sh
        while j < sh + 20000 and len(consts) < 8:
            j = p.find(b"\xf5\x1f", j, sh + 20000)
            if j < 0:
                break
            if is_const(u32(p, j)):
                consts.append(j)
            j += 1
        print(f"segid 202 sh={sh} cnt={cnt}")
        print("consts:", consts)
        for i, c in enumerate(consts):
            if i + 1 < len(consts):
                stride = consts[i+1] - c
                eid = u16(p, c + 4)
                tag = u16(p, c + 22)
                n1 = u16(p, c + 24)
                n2 = u16(p, c + 28)
                print(f"  CONST@{c} stride={stride} eid={eid} tag={tag} nodes=({n1},{n2})")
        break
