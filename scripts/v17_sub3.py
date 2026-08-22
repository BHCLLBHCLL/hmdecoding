
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
base = 8135747
print("sub3 head:", u32(p, base), u32(p, base+4), u32(p, base+8), "x=", d64(p, base+12))
# extend
cnt = 0
marks = {}
while base + cnt*68 + 68 <= len(p):
    rec = base + cnt*68
    nid = u32(p, rec)
    if 1 <= nid <= 10_000_000 and u32(p, rec+4) == 0 and 1 <= u32(p, rec+8) <= 16 and abs(d64(p, rec+12)) < 1e9:
        cnt += 1
        m = u32(p, rec+8)
        marks[m] = marks.get(m, 0) + 1
    else:
        break
print("sub3 count:", cnt, "marks:", dict(sorted(marks.items())))
last = base + (cnt-1)*68
print("sub3 last id:", u32(p, last), "at:", last)
# total: block A 116734 + sub3 cnt
print("total so far:", 116734 + cnt)
# next block after sub3?
nxt = last + 68
found = None
for j in range(nxt, min(nxt + 100, len(p) - 8)):
    pass
# look for next [id][0][k] block after sub3 end
for j in range(last + 68, min(last + 200000, len(p) - 8)):
    nid = u32(p, j)
    if 1 <= nid <= 10_000_000 and u32(p, j+4) == 0 and 1 <= u32(p, j+8) <= 16 and abs(d64(p, j+12)) < 1e9:
        ok = 0
        for k in range(1, 4):
            r2 = j + k*68
            if 1 <= u32(p, r2) <= 10_000_000 and u32(p, r2+4) == 0 and 1 <= u32(p, r2+8) <= 16:
                ok += 1
        if ok >= 2:
            found = j
            break
print("next block:", found)
