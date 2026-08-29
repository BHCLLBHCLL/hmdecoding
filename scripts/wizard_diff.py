
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments
from decoder import _parse_ansys2d_elems

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_wizard_2-d_tutorial.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = {k+1: u32(p, base + k*ns[3] + ns[4]) for k in range(ns[1])}
segs = find_elem_segments(p)
sh = segs[1][0]
got = _parse_ansys2d_elems(p, sh, 162, ns[1], rm, max_rec=None)
eids = set(got.keys())
all_e = set(range(41, 203))
missing = sorted(all_e - eids)
print("missing eids in seg2:", missing)
# the missing record - find its 0x30200B1F head position
for me in missing:
    # search for record: eid=me near sh
    for j in range(sh, sh+30000):
        if u32(p, j + 24) == me and p[j:j+4] == b"\x1f\x0b\x20\x30":
            print(f"  eid {me} head @{j}, rows={[u32(p, j+38+4*i) for i in range(6)]}")
            break
