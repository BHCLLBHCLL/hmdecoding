
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_wizard_2-d_tutorial.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = {k+1: u32(p, base + k*ns[3] + ns[4]) for k in range(ns[1])}
j = 24095
eid = u32(p, j + 24)
rows = []
for i in range(8):
    r = u32(p, j + 38 + 4*i)
    if not (1 <= r <= ns[1]):
        print(f"  break at i={i} r={r}")
        break
    rows.append(r)
print("eid:", eid, "rows:", rows, "len:", len(rows))
cfg = 104 if len(rows) == 4 else (103 if len(rows) == 3 else 0)
print("cfg:", cfg)
# what's at j+38+4*3 (the 0)? byte dump
print("bytes j+36..j+56:", p[j+36:j+56].hex(" "))
