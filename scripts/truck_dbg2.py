
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, row_map_from_nodes
from decoder import _parse_a_type, CONST, is_const

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = row_map_from_nodes(p, ns, base)
sh = 21436728
got = _parse_a_type(p, sh, 188, ns[1], rm, max_rec=5)
print("seg 2000290:", "OK" if got else "FAIL", len(got) if got else 0)
if not got:
    # trace
    s = sh + 24
    print("s:", s, "const:", is_const(u32(p, s)))
    nxt = None
    for j in range(s+24, s+300):
        if is_const(u32(p, j)):
            nxt = j; break
    d = nxt - s if nxt else None
    print("stride:", d)
    # flag candidates in [12, min(d, 84)]
    for off in range(12, min(d or 84, 84), 4):
        v = u32(p, s + off)
        f = v >> 16
        if 300 <= f <= 500 and (v & 0xFFFF) == 0:
            print(f"  flag cand @+{off}: 0x{v:08x} f={f}")
    fp = 44
    nodes_off = s + fp + 4
    n = 0
    while n < 12 and u32(p, nodes_off + 4*n) != 0:
        n += 1
    print("n at fp=44:", n, "nodes:", [u32(p, nodes_off+4*j) for j in range(min(n, 4))])
    print("check nodes_off+4n >= rec+rec_len:", nodes_off + 4*n >= s + d)
