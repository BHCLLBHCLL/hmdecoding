
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\crash_tubes.hm")
rec = 260238
eid = 1
for k in range(2280):
    ne = u16(p, rec + 2 + 16 + 4)
    if ne != eid + 1 or ne == 0:
        print(f"k={k}: eid={eid} next={ne} rec={rec}")
        for off in range(-4, 40, 2):
            print(f"  {off:+3d}: {u16(p, rec+off)}")
        if k > 100: break
    nxt = None
    for j in range(rec + 26, rec + 300):
        if (u16(p, j) != 0 and u16(p, j+2) != 0 and u16(p, j+4) == 0 and u16(p, j+6) != 0 and u16(p, j+8) == 0):
            nxt = j; break
    if nxt is None:
        print(f"k={k}: NO NEXT at rec={rec}")
        break
    rec = nxt
    eid = ne
print("last eid:", eid)
