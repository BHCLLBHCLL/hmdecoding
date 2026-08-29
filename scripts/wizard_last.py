
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_wizard_2-d_tutorial.hm")
ns = find_node_section(p)
segs = find_elem_segments(p)
sh = segs[1][0]; cnt = 162
pat = b"\x1f\x0b\x20\x30"
# enumerate seg2 records
recs = []
j = sh + 24
while True:
    j = p.find(pat, j, sh + 30000)
    if j < 0: break
    recs.append(j)
    j += 62
print("seg2 records:", len(recs))
for idx in (159, 160, 161):
    if idx < len(recs):
        j = recs[idx]
        eid = u32(p, j + 24)
        rows = [u32(p, j + 38 + 4*i) for i in range(6)]
        print(f"rec{idx}@{j}: eid={eid} rows={rows}")
