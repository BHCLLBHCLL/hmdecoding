
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64, find_node_section, parse_nodes

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\composites.hm")
ns = find_node_section(p)
print("ns:", ns)
if ns:
    hi, count, base, stride, idoff, chain = ns
    for k in range(124, 130):
        rec = base + k * stride
        nid = u32(p, rec + idoff)
        x = d64(p, rec + 12)
        print(f"  k={k}: id={nid} x={x:.5g}")
