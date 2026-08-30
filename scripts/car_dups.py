
import sys
sys.path.insert(0, "hmdecoder")
from collections import Counter
ids = [int(x) for x in open("output/ground_truth/car_ids.txt", encoding="utf-8").read().split() if x.strip().isdigit()]
c = Counter(ids)
dups = {e: n for e, n in c.items() if n > 1}
print("total ids:", len(ids), "unique:", len(c), "dup count:", len(dups))
# how many extra from dups
extra = sum(n-1 for n in dups.values())
print("extra (dup) count:", extra)
# which eids repeat
rep_sorted = sorted(dups.items(), key=lambda x: -x[1])
print("top repeating eids:", rep_sorted[:15])
print("multiplicity hist:", Counter(n for n in dups.values()).most_common())
