
import sys
sys.path.insert(0, "hmdecoder")
from decoder import decode
ids = []
for ln in open("output/ground_truth/truck_ids_full.txt", encoding="utf-8"):
    t = ln.strip()
    if t.isdigit(): ids.append(int(t))
oracle = set(ids)
m = decode(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
dec = set()
for e in m.elements:
    dec.add(e.id if hasattr(e,'id') else e[0])
print("oracle:", len(oracle), "decode unique:", len(dec))
missing = sorted(oracle - dec)
print("missing:", len(missing), "first20:", missing[:20])
extra = sorted(dec - oracle)
print("extra:", len(extra), "first10:", extra[:10])
