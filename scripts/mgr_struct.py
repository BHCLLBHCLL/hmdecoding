
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section_struct, parse_nodes, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
segs = find_node_section_struct(p, multi=True)
print("struct segs:")
for s in segs:
    n, b = parse_nodes(p, s)
    k = sorted(n.keys())
    print(f"  base={s[2]} stride={s[3]} cnt={s[1]} n={len(n)} ids={k[:3]}..{k[-2:] if len(k)>2 else ''}")
