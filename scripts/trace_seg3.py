
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u16, u32

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\crash_tubes.hm")
sh = 367482
s = sh + 24
rec = s + 8
eid = 7639
for k in range(900):
    ne = u16(p, rec + 22)
    if k < 2 or ne != eid + 1:
        print(f"k={k}: eid={eid} next={ne} rec={rec}")
    if ne == 0 or k > 870:
        break
    nxt = None
    for j in range(rec + 26, rec + 300):
        if (u16(p, j) != 0 and u16(p, j+2) != 0 and u16(p, j+4) == 0 and u16(p, j+6) != 0 and u16(p, j+8) == 0):
            nxt = j; break
    if nxt is None:
        print(f"  NO NEXT at k={k} rec={rec} eid={eid}")
        break
    rec = nxt
    eid = ne
print("seg3 end:", eid)
