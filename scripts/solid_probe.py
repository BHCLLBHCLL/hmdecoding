
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, find_node_section_struct

for fname, sub in [("solid_geom.hm", ""), ("solid_map.hm", "")]:
    p = load_payload(rf"C:\Program Files\Altair\2019\tutorials\hm\{fname}")
    ns = find_node_section(p)
    print(f"{fname}: ns={ns}")
    if ns:
        from decoder import parse_nodes
        n, b = parse_nodes(p, ns)
        print("  parse:", len(n))
    ss = find_node_section_struct(p, multi=True)
    print("  struct:", [(s[1], s[2], s[3]) for s in ss])
