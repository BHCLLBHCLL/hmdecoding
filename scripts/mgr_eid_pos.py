
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
lo, hi = 109769, min(124178, len(p) - 4)
pos = []
for eid in range(203, 213):
    hits = []
    for i in range(lo, hi):
        if u32(p, i) == eid:
            hits.append(i)
            if len(hits) >= 2: break
    pos.append((eid, hits))
for eid, h in pos:
    print(f"eid {eid}: {h}  spacing to next = {h[1]-h[0] if len(h)>1 else '?'}")
