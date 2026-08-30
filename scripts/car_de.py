
import sys
sys.path.insert(0, "hmdecoder")
from decoder import decode
from collections import Counter
m = decode(r"C:\Program Files\Altair\2019\tutorials\hm\car_section.hm")
de = Counter()
for e in m.elements:
    de[e.id if hasattr(e,'id') else e[0]] += 1
# oracle dups
oc = Counter(int(x) for x in open("output/ground_truth/car_ids.txt", encoding="utf-8").read().split() if x.strip().isdigit())
# compare eid 1..15
for eid in range(1, 16):
    print(f"eid {eid}: decode={de.get(eid,0)} oracle={oc.get(eid,0)}")
print("decode total:", sum(de.values()), "unique:", len(de))
# total extra missing
oc_extra = sum(n-1 for n in oc.values() if n > 1)
de_extra = sum(n-1 for n in de.values() if n > 1)
print("oracle dup-extra:", oc_extra, "decode dup-extra:", de_extra, "missing:", oc_extra - de_extra)
