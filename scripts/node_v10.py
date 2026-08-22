
import sys, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

def find_node_section_v10(p):
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
    for hi, count in hits[:600]:
        for base in range(hi - 32, hi + 48, 4):
            if base < 0:
                continue
            for stride, idoff, xoff, chain in ((52, 0, 12, False), (52, 4, 12, False), (92, 0, 12, False), (92, 4, 12, False), (56, 44, 4, True)):
                ok = 0; bad = 0
                for k in range(min(count, 60)):
                    rec = base + k * stride
                    if rec + stride > len(p):
                        break
                    x = d64(p, rec + xoff)
                    if chain:
                        tailok = u32(p, rec + 48) == 0 and u32(p, rec + 52) == 0
                        nid = u32(p, rec + 44) - 1
                    else:
                        tailok = True
                        nid = u32(p, rec + idoff)
                    if 1 <= nid <= 10_000_000 and abs(x) < 1e9 and tailok:
                        ok += 1
                    else:
                        bad += 1
                        if bad > 3:
                            break
                if ok >= 50 and bad <= 1:
                    return (hi, count, base, stride, idoff, "chain" if chain else "flat")
    return None

files = ["bottle.hm", "clip_refine.hm", "frame_assembly.hm", "housing.hm",
         "interfaces/lsdyna/head_2.hm", "fe_only.hm", "quality_index.hm",
         "s_bend_tube.hm", "yoke.hm", "propeller.hm", "dummy.hm",
         "molding1.hm", "truck.hm", "car_section.hm", "cover.hm",
         "interfaces/lsdyna/SEAT_MODEL.hm", "body_side.hm", "1d_elements.hm"]
for rel in files:
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{rel}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/{os.path.basename(rel)}"
    p = load_payload(path)
    res = find_node_section_v10(p)
    print(f"== {os.path.basename(rel)}: {res}")
