
import sys, re
sys.path.insert(0, "hmdecoder")
from decoder import decode
all_ids = [int(x) for x in open("output/ground_truth/mgr_ids.txt", encoding="utf-8").read().split() if x.strip().isdigit()]
oracle = set(all_ids)
m = decode(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
dec = set()
for e in m.elements:
    dec.add(e.id if hasattr(e, 'id') else e[0] if isinstance(e,(list,tuple)) else e.get('id'))
print("decode:", len(dec), "oracle:", len(oracle))
missing = sorted(oracle - dec)
print("missing:", missing)
extra = sorted(dec - oracle)
print("extra:", extra)
print("nodes:", len(m.nodes))
