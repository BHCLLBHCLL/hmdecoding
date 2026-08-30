
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, _scan_extra_node_segs

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
m_end = ns[2] + len(nodes) * ns[3]
excl = [(ns[2], ns[2] + 8)]
segs = _scan_extra_node_segs(p, excl, lo=max(0, m_end - 256), hi=m_end + 512*1024, min_nid=len(nodes)-16)
print("extra segs:")
for s in segs:
    n, b = parse_nodes(p, s)
    k = sorted(n.keys())
    print(f"  base={s[2]} stride={s[3]} cnt={s[1]} n={len(n)} ids={k[:3]}..{k[-2:] if len(k)>2 else ''}")
print("m_end:", m_end)
