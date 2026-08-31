
import sys
sys.path.insert(0, "hmdecoder")
from decoder import decode
m = decode(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
print("elements list len:", len(m.elements))
from collections import Counter
c = Counter(e.id if hasattr(e,'id') else e[0] for e in m.elements)
dups = {k:v for k,v in c.items() if v>1}
print("dup eids:", len(dups), "extra:", sum(v-1 for v in dups.values()))
# oracle count
ids = [int(x) for x in open("output/ground_truth/truck_ids_full.txt", encoding="utf-8").read().split() if x.strip().isdigit()]
print("oracle count:", len(ids))
