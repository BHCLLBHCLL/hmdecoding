
import sys, time
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, find_node_section, parse_nodes, find_elem_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
t0 = time.time()
segs = find_elem_segments(p)
print(f"v17 elem segs: {len(segs)} in {time.time()-t0:.1f}s")
from collections import Counter
xs = Counter(s[4] for s in segs)
print("X distribution:", dict(xs))
total = sum(s[3] for s in segs)
print("total count:", total)
print("first segs:", [(s[1], s[3], s[4], s[5]) for s in segs[:6]])
