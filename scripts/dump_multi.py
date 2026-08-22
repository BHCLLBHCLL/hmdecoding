
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32

def dump_elem_secs(path, maxdump=80):
    p = load_payload(path)
    print(f"== {path.split('/')[-1]} db={struct_d64(p)} len={len(p)}")
    hits = []
    i = 0
    while i < len(p) - 16:
        if u32(p, i) == 997:
            cfg = u32(p, i + 8)
            cnt = u32(p, i + 12)
            if cfg in (170, 171, 172, 173, 174, 175, 176, 275, 276, 277) and 1 <= cnt <= 10_000_000:
                hits.append((i, u32(p, i + 4), cfg, cnt, u32(p, i + 16), u32(p, i + 20)))
        i += 1
    for h, seg, cfg, cnt, a, b in hits[:8]:
        print(f"  [997]@{h} seg={seg} cfg+71={cfg} count={cnt} next=[{a},{b}]")
        for k in range(0, min(maxdump, 4) * 16, 16):
            ws = [u32(p, h + 24 + k + j) for j in range(0, 16, 4)]
            print(f"    +{24+k:4d}: {ws}")

import struct
def struct_d64(p): return struct.unpack_from("<d", p, 4)[0]

for f in [r"C:\Program Files\Altair\2019\tutorials\hm\bottle.hm",
          r"C:\Program Files\Altair\2019\tutorials\hm\clip_refine.hm",
          r"C:\Program Files\Altair\2019\tutorials\hm\frame_assembly.hm",
          r"C:\Program Files\Altair\2019\tutorials\hm\housing.hm",
          r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\head_2.hm"]:
    dump_elem_secs(f)
