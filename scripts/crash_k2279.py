
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, find_node_section
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\crash_tubes.hm")
ns = find_node_section(p)
segs = find_elem_segments(p)
sh = segs[0][0]
s = sh + 24
rec = s + 8
k = 0
# simulate _parse_b_slots tracking to find k=2279 rec
prev = None
for k in range(2280):
    slots = 0
    while slots < 12 and u16(p, rec + 2 + 4*slots) != 0 and u16(p, rec + 2 + 4*slots + 2) == 0:
        slots += 1
    rows = [u16(p, rec + 2 + 4*j) for j in range(slots)] if slots else []
    if k in (2278, 2279):
        print(f"k={k} rec={rec} slots={slots} rows={rows} valid={all(1<=r<=ns[1] for r in rows)}")
    # nxt
    nxt = None
    for j in range(rec + 2 + 4*slots + 8, min(rec + 50000, len(p)-8)):
        if not (u16(p, j) != 0 and u16(p, j+2) != 0 and u16(p, j+4) == 0 and u16(p, j+6) != 0 and u16(p, j+8) == 0):
            continue
        t_slots = 0
        while t_slots < 12 and u16(p, j + 2 + 4*t_slots) != 0 and u16(p, j + 2 + 4*t_slots + 2) == 0:
            t_slots += 1
        t_nds = [u16(p, j + 2 + 4*t) for t in range(t_slots)]
        if not t_slots or not all(1 <= r <= ns[1] for r in t_nds): continue
        nxt = j
        break
    if nxt is None:
        print(f"  k={k}: nxt None -> stop"); break
    rec = nxt
