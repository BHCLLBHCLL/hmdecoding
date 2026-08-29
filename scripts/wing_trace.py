
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments
from decoder import _parse_a_geom

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = {k+1: u32(p, base + k*ns[3] + ns[4]) for k in range(ns[1])}
segs = find_elem_segments(p)
sh = segs[0][0]; nxt = segs[1][0]
got = _parse_a_geom(p, sh, nxt, 475, ns[1], rm, max_rec=None)
print("a_geom full:", len(got) if got else 0)
# trace where it stops
MARK = b"\xe4\x0b\x04\x1a"
prev = None
j = sh + 24
n = 0
stops = []
while j < nxt:
    j = p.find(MARK, j, nxt)
    if j < 0: break
    if prev is not None and not (68 <= j - prev <= 80):
        stops.append((j, j - prev))
        j += 1
        continue
    eid = u32(p, j + 36)
    rows = []
    for i in range(8):
        r = u32(p, j + 48 + 4*i) >> 16
        if not (1 <= r <= ns[1]):
            break
        rows.append(r)
    if rows and 0 < eid < 10_000_000:
        prev = j
        n += 1
    else:
        stops.append((j, -2, eid, rows[:3]))
    j += 1
print("parsed:", n, "stops:", len(stops))
print("first stops:", stops[:5])
