
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
b = 21935103
cnt = 0
marks = {}
while b + cnt*92 + 92 <= len(p):
    rec = b + cnt*92
    nid = u32(p, rec)
    if 1 <= nid <= 10_000_000 and u32(p, rec+4) == 0 and 1 <= u32(p, rec+8) <= 64 and abs(d64(p, rec+12)) < 1e9:
        cnt += 1
        m = u32(p, rec+8)
        marks[m] = marks.get(m, 0) + 1
    else:
        break
print("segment B 92B: cnt =", cnt, "marks:", dict(sorted(marks.items())))
last = b + (cnt-1)*92 if cnt else None
print("last id:", u32(p, last) if last else None)
# next segment after B?
nxt = None
if last:
    for j in range(last + 92, min(last + 50000, len(p) - 8)):
        nid = u32(p, j)
        if 1 <= nid <= 10_000_000 and u32(p, j+4) == 0 and 1 <= u32(p, j+8) <= 64 and abs(d64(p, j+12)) < 1e9:
            ok = 0
            for k in range(1, 3):
                r2 = j + k*92
                if 1 <= u32(p, r2) <= 10_000_000 and u32(p, r2+4) == 0 and 1 <= u32(p, r2+8) <= 64:
                    ok += 1
            if ok >= 1:
                nxt = j
                break
    print("next 92B block:", nxt)
# also check 68B variant for segment B area? and another 68B segment
