
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u16, u32

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\crash_tubes.hm")
# seg4 @397218
sh = 397218
s = sh + 24
rec = s + 8
eid = 8513
for k in range(900):
    ne = u16(p, rec + 22)
    if k < 3 or ne != eid + 1:
        print(f"k={k}: eid={eid} next={ne}")
    nxt = None
    for j in range(rec + 26, rec + 300):
        if (u16(p, j) != 0 and u16(p, j+2) != 0 and u16(p, j+4) == 0 and u16(p, j+6) != 0 and u16(p, j+8) == 0):
            nxt = j; break
    if nxt is None:
        print(f"  NO NEXT at k={k} rec={rec}")
        for off in range(0, 60, 2):
            print(f"  {off:+3d}: {u16(p, rec+off)}")
        break
    rec = nxt
    eid = ne
print("seg4 end eid:", eid)

# abaqus3_0 seg1
p2 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\abaqus3_0tutorial.hm")
import struct
print("db:", struct.unpack_from("<d", p2, 4)[0])
hits = [i for i in range(len(p2)-24) if u32(p2, i) == 997]
print("997 segs:", [(h, [u32(p2, h+j*4) for j in range(6)]) for h in hits[:4]])
