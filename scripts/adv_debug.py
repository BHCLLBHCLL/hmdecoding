
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\crash_tubes.hm")
sh = 260206
s = sh + 24
rec = s + 8
for k in range(6):
    slots = 0
    while slots < 12 and u16(p, rec + 2 + 4*slots) != 0 and u16(p, rec + 2 + 4*slots + 2) == 0:
        slots += 1
    ne = u16(p, rec + 2 + 4*slots + 4)
    print(f"k={k}: rec={rec} slots={slots} next={ne} expect={1+k+1}")
    # find first candidate & its next
    found = None
    for j in range(rec + 2 + 4*slots + 8, rec + 200):
        if u16(p, j) != 0 and u16(p, j+2) != 0 and u16(p, j+4) == 0 and u16(p, j+6) != 0 and u16(p, j+8) == 0:
            t_slots = 0
            while t_slots < 12 and u16(p, j + 2 + 4*t_slots) != 0 and u16(p, j + 2 + 4*t_slots + 2) == 0:
                t_slots += 1
            t_ne = u16(p, j + 2 + 4*t_slots + 4)
            print(f"    cand@{j-rec} slots={t_slots} t_ne={t_ne}")
            found = j
            break
    if found is None:
        print("    NO CAND"); break
    rec = found
