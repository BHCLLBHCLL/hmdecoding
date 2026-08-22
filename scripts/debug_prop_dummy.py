
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

def dump(p, seg, label, nb=56):
    print(f"== {label} seg@{seg} header={[u32(p, seg+j*4) for j in range(6)]}")
    s = seg + 24
    for k in range(0, nb, 4):
        print(f"  +{k:3d}: {p[s+k:s+k+4].hex()} u32={u32(p,s+k):>9d} u16=({u16(p,s+k):>4d},{u16(p,s+k+2):>4d})")

p1 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\propeller.hm")
dump(p1, 480895, "propeller seg3")
print("E1605 nodes [1380,1522,1509] search:", end=" ")
h = [i for i in range(len(p1)-12) if u32(p1,i)==1380 and u32(p1,i+4)==1522 and u32(p1,i+8)==1509]
print(h[:3], "rel to seg:", [x-480895 for x in h[:3]])

p2 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\dummy.hm")
for sh, name in [(228589, "dummy seg73"), (258377, "dummy seg?")]:
    dump(p2, sh, name, 48)
# find all 997 with segid>1e6
hits = []
i = 0
while i < len(p2) - 24:
    if u32(p2, i) == 997:
        hits.append((i, u32(p2, i+4), u32(p2, i+12), u32(p2, i+16), u32(p2, i+20)))
    i += 1
print("all 997 segs:", hits[:6])
