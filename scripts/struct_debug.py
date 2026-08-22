
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64, find_node_section_struct

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
res = find_node_section_struct(p)
print("struct:", res)
if res:
    hi, count, base, stride, idoff, chain = res
    for k in range(3):
        rec = base + k * stride
        print(f"  rec{k}: id={u32(p, rec+idoff)} x={d64(p, rec+12):.4g}")
# manual: check the known location 197811
for off in (197811, 197812, 197808):
    nid = u32(p, off)
    print(f"@{off}: id={nid} +4={u32(p, off+4)} +8={u32(p, off+8)}")
