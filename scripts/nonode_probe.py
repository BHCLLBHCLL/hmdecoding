
import sys, json, os, struct
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section, parse_nodes

# 1) NO-NODE files: db version + head dump
for fname in ["molding1.hm", "truck.hm", "car_section.hm", "cover.hm", "SEAT_MODEL.hm"]:
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{fname}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/{fname}"
    p = load_payload(path)
    print(f"== {fname}: db={d64(p,4)} len={len(p)}")
    # scan for [1][136][count] with any alignment
    found = []
    for i in range(0, len(p) - 40, 2):
        if u32(p, i + 8) == 1 and u32(p, i + 12) == 136:
            n = u32(p, i + 16)
            if 1 <= n <= 10_000_000:
                found.append((i, n))
                if len(found) > 4: break
    print("  [1][136] candidates:", found[:5])
    # 997 element segments
    segs = []
    i = 0
    while i < len(p) - 24:
        if u32(p, i) == 997:
            X = u32(p, i + 16)
            if X in (2, 3):
                segs.append((i, u32(p, i + 4), u32(p, i + 8), u32(p, i + 12), X, u32(p, i + 20)))
                if len(segs) > 6: break
        i += 1
    print("  elem segs:", segs[:6])
