
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm")
# search rows [570,598,956,569] as u32 sequence and u16 pairs
seq = [570, 598, 956, 569]
for mode in ("u32", "u16"):
    hits = []
    for i in range(0, len(p) - 4*len(seq)):
        if mode == "u32":
            ok = all(u32(p, i + j*4) == seq[j] for j in range(len(seq)))
        else:
            ok = all(u16(p, i + j*4) == seq[j] for j in range(len(seq)))
        if ok:
            hits.append((i, mode))
    print(f"{mode}: {hits[:6]}")
# also u16 pairs [attr,row][attr,row]... rows at odd u16
hi = []
for i in range(0, len(p) - 2*len(seq)):
    if all(u16(p, i + j*4 + 2) == seq[j] for j in range(len(seq))):
        hi.append(i)
print("u16 row at +2 offset:", hi[:6])
