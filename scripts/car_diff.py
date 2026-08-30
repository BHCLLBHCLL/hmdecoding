
import sys
sys.path.insert(0, "hmdecoder")
from decoder import decode

m = decode(r"C:\Program Files\Altair\2019\tutorials\hm\car_section.hm")
print("type:", type(m.elements))
if m.elements:
    print("first:", m.elements[0])
    e0 = m.elements[0]
    print("elem0 type:", type(e0), "dict?", getattr(e0, "id", None))
ids = []
for ln in open("output/ground_truth/car_ids.txt", encoding="utf-8"):
    ln = ln.strip()
    if ln.isdigit():
        ids.append(int(ln))
oracle = set(ids)
dec = set()
for e in m.elements:
    eid = e.id if hasattr(e, "id") else (e[0] if isinstance(e, (list, tuple)) else e.get("id"))
    dec.add(eid)
print("decode ids:", len(dec))
missing = sorted(oracle - dec)
print("missing count:", len(missing), "first20:", missing[:20])
