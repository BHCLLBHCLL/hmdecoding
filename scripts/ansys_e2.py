
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_wizard_2-d_tutorial.hm")
# search E2 [3,4,32,29] and E3 [4,5,35,32]
for name, seq in (("E2", [3,4,32,29]), ("E3", [4,5,35,32])):
    hits = [i for i in range(0, len(p)-16) if all(u32(p, i+j*4) == seq[j] for j in range(4))]
    print(f"{name} hits:", hits[:4])
# dump from E1 (21575) backward 40B and forward 100B
h = 21575 - 40
print(f"--- E1 area from {h} ---")
for k in range(0, 140, 4):
    off = h + k
    print(f"  {off-21575:+5d}: {p[off:off+4].hex()} u32={u32(p,off):>10d}")
