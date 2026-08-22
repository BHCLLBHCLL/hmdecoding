
import gzip, struct, sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section

def scan(path):
    p = load_payload(path)
    ns = find_node_section(p)
    print(f"== {path.split('/')[-1]} db={d64(p,4)} len={len(p)}")
    if not ns:
        print("  NO NODE SECTION")
        return
    hdr, ncount, shift, idoff, coordoff = ns[0]
    print(f"  node hdr@{hdr} count={ncount} shift={shift}")
    hits = []
    for i in range(hdr, min(len(p) - 16, hdr + 60_000_000)):
        if u32(p, i) == 997:
            hits.append(i)
    print(f"  997 hits: {len(hits)} first 12: {hits[:12]}")
    for h in hits[:6]:
        print(f"   @{h}: {[u32(p, h + 4*j) for j in range(0, 8)]}")

for f in [r"C:\Program Files\Altair\2019\tutorials\hm\body_side.hm",
          r"C:\Program Files\Altair\2019\tutorials\hm\bottle.hm",
          r"C:\Program Files\Altair\2019\tutorials\hm\clip_refine.hm",
          r"C:\Program Files\Altair\2019\tutorials\hm\frame_assembly.hm",
          r"C:\Program Files\Altair\2019\tutorials\hm\housing.hm",
          r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\head_2.hm"]:
    scan(f)
