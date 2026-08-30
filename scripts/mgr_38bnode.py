
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
# 38B node seg @110871
b = 110871
for k in range(5):
    rec = b + k*38
    nid = u32(p, rec)
    mk = u32(p, rec+8)
    x = d64(p, rec+12)
    print(f"k={k}: id={nid} mark={mk} x={x:.4g} y={d64(p,rec+20):.4g} z={d64(p,rec+28):.4g}")
# extend to find count
cnt = 0
while b + cnt*38 + 38 <= len(p):
    rec = b + cnt*38
    nid = u32(p, rec)
    if 1 <= nid <= 10_000_000 and u32(p, rec+4) == 0 and abs(d64(p, rec+12)) < 1e9:
        cnt += 1
    else:
        break
print("38B node seg count:", cnt, "last id:", u32(p, b + (cnt-1)*38) if cnt else None)
# also id 168..195 seg
hits168 = [i for i in range(0, len(p)-40) if u32(p, i) == 168 and u32(p, i+4) == 0 and abs(d64(p, i+12)) < 1e9]
print("id 168 hits:", hits168[:3])
