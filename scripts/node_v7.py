
import sys, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

def find_node_section_v7(p, limit=None):
    lim = limit or (len(p) - 100)
    hits = []
    i = 0
    while i < lim - 40:
        if u32(p, i) == 136:
            n = u32(p, i + 4)
            if 1 <= n <= 10_000_000:
                hits.append((i, n))
        i += 4
    # prioritize larger counts, all candidates
    hits.sort(key=lambda h: -h[1])
    for hi, count in hits[:200]:
        for base in range(hi - 32, hi + 44, 4):
            if base < 0: continue
            # 52B: id@+4 x@+12 | 92B: same + 40B extra | 132B | 56B no-id
            for stride, idoff, xoff, recname in ((52, 4, 12, "52"), (92, 4, 12, "92"), (132, 4, 12, "132"), (56, None, 0, "56")):
                ok = 0; bad = 0
                for k in range(min(count, 80)):
                    rec = base + k * stride
                    if rec + stride > len(p):
                        break
                    x = d64(p, rec + xoff)
                    nid = u32(p, rec + idoff) if idoff is not None else k + 1
                    if 1 <= nid <= 10_000_000 and abs(x) < 1e9:
                        ok += 1
                    else:
                        bad += 1
                        if bad > 3:
                            break
                if ok >= 60 and bad <= 1:
                    return (hi, count, base, stride, idoff, recname)
    return None

files = ["bottle.hm", "clip_refine.hm", "frame_assembly.hm", "housing.hm",
         "interfaces/lsdyna/head_2.hm", "fe_only.hm", "quality_index.hm",
         "s_bend_tube.hm", "yoke.hm", "propeller.hm", "dummy.hm",
         "molding1.hm", "truck.hm", "car_section.hm", "cover.hm",
         "interfaces/lsdyna/SEAT_MODEL.hm", "body_side.hm", "interfaces/madymo/leg_geom.hm", "1d_elements.hm"]
for rel in files:
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{rel}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/{os.path.basename(rel)}"
    if not os.path.exists(path):
        path = rel if os.path.exists(rel) else None
    if not path:
        print(f"== {os.path.basename(rel)}: MISSING"); continue
    p = load_payload(path)
    res = find_node_section_v7(p)
    print(f"== {os.path.basename(rel)}: {res}")
