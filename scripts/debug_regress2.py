
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

# WS: verify base candidates for [136]@602381
p = load_payload("WS_3.2_3d_tetra_finish.hm")
hi, count = 602381, 6408
for base in range(hi - 32, hi + 48, 4):
    for stride, idoff, xoff in ((52, 0, 12), (52, 4, 12), (52, 8, 20)):
        ok = 0; bad = 0
        for k in range(min(count, 40)):
            rec = base + k * stride
            nid = u32(p, rec + idoff)
            x = d64(p, rec + xoff)
            if 1 <= nid <= 10_000_000 and abs(x) < 1e9:
                ok += 1
            else:
                bad += 1
                if bad > 2: break
        if ok >= 35:
            print(f"  WS: base={base} stride={stride} idoff={idoff} xoff={xoff} ok={ok}")
print("first rec id check at 602381+24:", u32(p, 602405), u32(p, 602409))

# body_side chain
p2 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\body_side.hm")
sh = 390741
s = sh + 28
rec = s
brk = None
for k in range(200):
    if u32(p2, rec) != 0x70241FF5:
        brk = (k, rec)
        break
    rec += 76
print("\nbody_side first break:", brk)
if brk:
    b = brk[1]
    for off in range(-8, 40, 4):
        print(f"  {off:+4d}: {p2[b+off:b+off+4].hex()} u32={u32(p2, b+off)}")
