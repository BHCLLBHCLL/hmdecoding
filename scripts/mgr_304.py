
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
base = 109769 + (304-203)*38
print("eid 304 expected @", base)
for k in range(-20, 100, 4):
    o = base + k
    print(f"  {k:+4d}: {p[o:o+4].hex()} u32={u32(p,o):>10d} u16=({u16(p,o):>5d},{u16(p,o+2):>5d}) if o+4<len p")
