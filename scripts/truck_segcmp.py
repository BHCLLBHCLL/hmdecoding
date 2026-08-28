
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
# find seg 1 and seg 2000001 headers
for target in (1, 2000001, 2000280):
    sh = None
    i = 0
    while i < len(p) - 24:
        if u32(p, i) == 997 and u32(p, i+4) == target:
            sh = i; break
        i += 1
    if not sh:
        print(f"seg {target}: NOT FOUND"); continue
    print(f"== seg {target} @{sh}: header={[u32(p, sh+j*4) for j in range(6)]}")
    s = sh + 24
    for k in range(0, 52, 4):
        print(f"  +{k:3d}: {p[s+k:s+k+4].hex()} u32={u32(p,s+k):>9d}")
