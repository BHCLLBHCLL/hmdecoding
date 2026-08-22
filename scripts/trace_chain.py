
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\crash_tubes.hm")
rec = 260238
eid = 1
for k in range(12):
    X = u16(p, rec)
    n1 = u16(p, rec+2)
    ne = u16(p, rec + 2 + 16 + 4)
    print(f"k={k}: rec={rec} X={X} n1={n1} next={ne} (eid={eid})")
    if ne != eid + 1:
        print(f"   CHAIN BREAK at k={k}")
    nxt = None
    for j in range(rec + 2 + 16 + 8, rec + 300):
        if u16(p, j) != 0 and u16(p, j+2) == 0 and u16(p, j+4) != 0 and u16(p, j+6) == 0:
            nxt = j; break
    if nxt is None:
        print("   NO NEXT RECORD"); break
    rec = nxt
    eid = ne
