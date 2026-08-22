
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, CONST

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\body_side.hm")
sh = 390741
# find CONST starts
consts = [i for i in range(sh+16, sh+200) if u32(p, i) == CONST]
print("CONST positions rel sh:", [c-sh for c in consts[:8]])
s = sh + 52
print("s = sh+52, eid@+4:", u32(p, s+4))
# record trace: 8 records
rec = s
for k in range(8):
    print(f"k={k} rec={rec-sh:+4d}: CONST={u32(p,rec)==CONST} eid={u32(p,rec+4)}")
    nxt = None
    for j in range(rec+24, rec+200):
        if u32(p, j) == CONST:
            nxt = j; break
    print(f"   nxt rel: {nxt-rec if nxt else None}")
    if nxt is None: break
    rec = nxt
