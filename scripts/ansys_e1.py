
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_wizard_2-d_tutorial.hm")
h = 21550
for k in range(0, 100, 4):
    print(f"  {h+k-21575:+5d}: {p[h+k:h+k+4].hex()} u32={u32(p,h+k):>10d} u16=({u16(p,h+k):>5d},{u16(p,h+k+2):>5d})")
