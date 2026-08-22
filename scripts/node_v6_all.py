
import sys, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

def find_node_section_v6(p, limit=None):
    lim = limit or (len(p) - 100)
    hits = []
    i = 0
    while i < lim - 40:
        if u32(p, i) == 136:
            n = u32(p, i + 4)
            if 1 <= n <= 10_000_000:
                hits.append((i, n))
        i += 4
    for hi, count in hits[:40]:
        for base in range(hi - 32, hi + 40, 4):
            if base < 0: continue
            for stride, idoff, xoff in ((52, 8, 20), (92, 8, 20), (56, None, 0), (132, 8, 20)):
                ok = 0; bad = 0
                for k in range(min(count, 60)):
                    rec = base + k * stride
                    if rec + stride > len(p):
                        break
                    x = d64(p, rec + xoff)
                    nid = u32(p, rec + idoff) if idoff is not None else k + 1
                    if 1 <= nid <= 10_000_000 and abs(x) < 1e9:
                        ok += 1
                    else:
                        bad += 1
                        if bad > 4:
                            break
                if ok >= 45 and bad <= 1:
                    return (hi, count, base, stride, idoff)
    # structural fallback
    for stride, idoff, xoff in ((52, 8, 20), (92, 8, 20), (56, None, 0)):
        base = 0
        while base + 60 * stride <= len(p):
            ok = 0
            for k in range(30):
                rec = base + k * stride
                x = d64(p, rec + xoff)
                nid = u32(p, rec + idoff) if idoff is not None else k + 1
                if 1 <= nid <= 10_000_000 and abs(x) < 1e9 and (idoff is not None or u32(p, rec) != 0):
                    ok += 1
                else:
                    break
            if ok >= 25:
                cnt = ok
                while base + cnt * stride + stride <= len(p):
                    rec = base + cnt * stride
                    x = d64(p, rec + xoff)
                    nid = u32(p, rec + idoff) if idoff is not None else cnt + 1
                    if 1 <= nid <= 10_000_000 and abs(x) < 1e9:
                        cnt += 1
                    else:
                        break
                return (None, cnt, base, stride, idoff)
            base += 4
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
        print(f"== {rel}: MISSING"); continue
    p = load_payload(path)
    res = find_node_section_v6(p)
    print(f"== {os.path.basename(rel)}: {res}")
