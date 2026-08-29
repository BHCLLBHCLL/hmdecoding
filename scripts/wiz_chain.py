
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_elem_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_wizard_2-d_tutorial.hm")
segs = find_elem_segments(p)
sh = segs[1][0]
pat = b"\x1f\x0b\x20\x30"
# find all heads from sh+24, but seg2 might start differently
recs = []
j = sh
while True:
    j = p.find(pat, j, sh + 30000)
    if j < 0: break
    eid = u32(p, j + 24)
    recs.append((j, eid))
    j += 62
print("recs count:", len(recs))
# find eid 58 position
for idx, (j, eid) in enumerate(recs):
    if eid == 58:
        print(f"eid58 at idx {idx} j={j}")
# print records idx 15..20 to see around 57/58/59
for idx in range(15, 21):
    if idx < len(recs):
        j, eid = recs[idx]
        print(f"idx{idx}@{j}: eid={eid} row0={u32(p,j+38)}")
