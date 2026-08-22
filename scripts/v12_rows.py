
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\c_channel-tcl.hm")
ns = find_node_section(p)
print("ns:", ns)
nodes, base = parse_nodes(p, ns)
ids = [u32(p, base + k * 52 + ns[4]) for k in range(ns[1])]
print("node ids first:", ids[:5], "count:", len(ids))
# E2746 nodes = [3016, 2892, 2891, 3012] -> rows?
row_of = {nid: k+1 for k, nid in enumerate(ids)}
print("row of 3016:", row_of.get(3016), "of 2892:", row_of.get(2892), "of 2891:", row_of.get(2891), "of 3012:", row_of.get(3012))
print("expect rows [246, 505, 558, 247] if u16 slot theory holds")
