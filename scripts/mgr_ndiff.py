
import sys
sys.path.insert(0, "hmdecoder")
from decoder import decode
oracle = set(int(x) for x in open("output/ground_truth/mgr_node_ids.txt", encoding="utf-8").read().split() if x.strip().isdigit())
m = decode(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
dec = set(m.nodes.keys())
print("decode nodes:", len(dec), "oracle:", len(oracle))
missing = sorted(oracle - dec)
print("missing ids:", missing)
# check decode nodes id range
if dec: print("decode id range:", min(dec), max(dec))
