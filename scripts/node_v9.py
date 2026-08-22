
import sys, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

def find_node_section_v9(p):
    hits = []
    start = 0
    while True:
        i = p.find(b"\x88\x00\x00\x00", start)
        if i < 0:
            break
        n = u32(p, i + 4)
        if 1 <= n <= 10_000_000:
            hits.append((i, n))
        start = i + 1
    hits.sort(key=lambda h: -h[1])
    checked = set()
    for hi, count in hits[:500]:
        for base in range(hi - 32, hi + 48, 4):
            if base < 0:
                continue
            for stride, idoff, xoff, tailreq in ((52, 0, 12, False), (52, 4, 12, False), (92, 0, 12, False), (92, 4, 12, False), (56, None, 0, True)):
                key = (base, stride, idoff)
                if key in checked:
                    continue
                checked.add(key)
                ok = 0; bad = 0
                for k in range(min(count, 60)):
                    rec = base + k * stride
                    if rec + stride > len(p):
                        break
                    x = d64(p, rec + xoff)
                    nid = u32(p, rec + idoff) if idoff is not None else k + 1
                    if tailreq:
                        tailok = all(u32(p, rec + 24 + j * 4) == 0 for j in range(8))
                    else:
                        tailok = True
                    if 1 <= nid <= 10_000_000 and abs(x) < 1e9 and tailok:
                        ok += 1
                    else:
                        bad += 1
                        if bad > 3:
                            break
                if ok >= 50 and bad <= 1:
                    return (hi, count, base, stride, idoff)
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
    res = find_node_section_v9(p)
    print(f"== {os.path.basename(rel)}: {res}")
