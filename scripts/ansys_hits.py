
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_wizard_2-d_tutorial.hm")
pat = b"\x1f\x0b\x20\x30"
hits = []
start = 0
while True:
    i = p.find(pat, start)
    if i < 0: break
    hits.append(i)
    start = i + 1
print("0x30200B1F hits:", len(hits), "first:", hits[:8])
print("spacings:", [hits[i+1]-hits[i] for i in range(min(10, len(hits)-1))])
# dump first record
if hits:
    h = hits[0]
    print(f"--- record @{h} ---")
    for k in range(0, 48, 4):
        print(f"  +{k:3d}: {p[h+k:h+k+4].hex()} u32={u32(p,h+k):>10d}")
