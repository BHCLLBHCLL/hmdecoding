
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64, find_node_section, parse_nodes

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
ns = find_node_section(p)
print("ns:", ns)
hi, count, base, stride, idoff, chain = ns
nodes, b = parse_nodes(p, ns)
print("parsed nodes:", len(nodes))
# check last few records
for k in range(count-3, count):
    rec = base + k*stride
    nid = u32(p, rec+idoff)
    x = d64(p, rec+12)
    print(f"k={k}: rec={rec} id={nid} x={x:.4g} valid={1<=nid<=10_000_000 and abs(x)<1e9}")
# dump last record bytes
rec = base + (count-1)*stride
print("last rec bytes:", p[rec:rec+stride].hex(" "))
