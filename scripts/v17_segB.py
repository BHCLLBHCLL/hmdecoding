
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
for base in (21935103, 197811):
    print(f"@{base}: id={u32(p, base)} mark={u32(p, base+8)} x={d64(p, base+12):.4g}")
# extend from 21935103
b = 21935103
cnt = 0
marks = {}
while b + cnt*68 + 68 <= len(p):
    rec = b + cnt*68
    nid = u32(p, rec)
    if 1 <= nid <= 10_000_000 and u32(p, rec+4) == 0 and 1 <= u32(p, rec+8) <= 16 and abs(d64(p, rec+12)) < 1e9:
        cnt += 1
        m = u32(p, rec+8)
        marks[m] = marks.get(m, 0) + 1
    else:
        break
print("segment B: cnt =", cnt, "marks:", dict(sorted(marks.items())))
print("segment B first ids:", [u32(p, b + k*68) for k in range(3)])
print("segment B last id:", u32(p, b + (cnt-1)*68) if cnt else None)
