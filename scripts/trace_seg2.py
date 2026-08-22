
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u16, u32

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\crash_tubes.hm")
sh = 337746
s = sh + 24
print("seg2 s:", [u32(p, s+j*4) for j in range(4)])
rec = s + 8
for k in range(8):
    X = u16(p, rec)
    n1 = u16(p, rec+2)
    ne = u16(p, rec + 2 + 16 + 4)
    print(f"k={k}: rec={rec} X={X} n1={n1} next={ne}")
    nxt = None
    for j in range(rec + 26, rec + 300):
        if (u16(p, j) != 0 and u16(p, j+2) != 0 and u16(p, j+4) == 0 and u16(p, j+6) != 0 and u16(p, j+8) == 0):
            nxt = j; break
    if nxt is None:
        print("   NO NEXT"); break
    rec = nxt
