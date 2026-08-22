
import sys, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

for fname in ["1d_elements.hm", "body_side.hm", "bottle.hm", "s_bend_tube.hm", "leg_geom.hm"]:
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{fname}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/{fname}"
    p = load_payload(path)
    hits = []
    start = 0
    while True:
        i = p.find(b"\x88\x00\x00\x00", start)
        if i < 0: break
        n = u32(p, i + 4)
        hits.append((i, n))
        start = i + 1
    good = [(i, n) for i, n in hits if 1 <= n <= 10_000_000]
    print(f"== {fname}: [136] hits={len(hits)} plausible={len(good)} first15={good[:15]}")
