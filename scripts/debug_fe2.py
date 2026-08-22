
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\fe_only.hm")
rec = 4748169
print("bytes rec+86..rec+98:", p[rec+86:rec+98].hex(" "))
for z in (rec+94, rec+92, rec+90, rec+88, rec+86, rec+84, rec+82):
    v = u16(p, z)
    v2 = u16(p, z+2)
    print(f"  z=+{z-rec}: u16={v} u16(z+2)={v2} -> {(v, v2)}")
# also raw hex of last 16 bytes
print("last 20B:", p[rec+78:rec+98].hex(" "))
