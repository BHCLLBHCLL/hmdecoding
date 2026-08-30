
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
# search id 232 record: u32 232 followed by [0][k] and coords
hits = []
for i in range(0, len(p) - 40):
    if u32(p, i) == 232 and u32(p, i+4) == 0 and abs(d64(p, i+12)) < 1e9:
        hits.append((i, u32(p, i+8)))
print("id 232 hits:", hits[:5])
# also id 233 (should be adjacent in same segment)
for nid in (233, 234):
    h2 = [i for i in range(0, len(p)-40) if u32(p, i) == nid and u32(p, i+4) == 0 and abs(d64(p, i+12)) < 1e9]
    print(f"id {nid}: {h2[:3]}")
