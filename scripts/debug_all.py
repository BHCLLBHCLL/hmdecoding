
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes

# --- fe_only trace ---
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\fe_only.hm")
sh = 4748145
s = sh + 24
print("fe_only: flag@+8 =", u16(p, s+8), "config =", u16(p, s+8)-256)
rec = s
for k in range(3):
    print(f"  k={k} rec={rec}: u32={u32(p,rec)},{u32(p,rec+4)} flag={u16(p,rec+8)} nds0={[u32(p,rec+10+j*4) for j in range(8)]}")
    nxt = None
    for j in range(rec + 50, rec + 500):
        if u32(p, j) == 0 and u32(p, j+4) == 0 and 300 <= u16(p, j+8) <= 500:
            nxt = j; break
    print(f"     nxt={nxt} stride={nxt-rec if nxt else None}")
    if nxt is None: break
    z = None
    for zz in range(rec + 42, nxt):
        if u32(p, zz) == 0:
            z = zz; break
    print(f"     z={z} ne={u16(p, z+4) if z else None} ne2={u16(p, z+6) if z else None}")
    rec = nxt

# --- propeller seg3 trace ---
p2 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\propeller.hm")
sh2 = 480895
s2 = sh2 + 24
print("\npropeller seg3: flag@+8 =", u16(p2, s2+8))
rec = s2
for k in range(3):
    fl = u16(p2, rec+8)
    n = {359: 3, 360: 4}.get(fl - 256, 4)
    print(f"  k={k} rec={rec} flag={fl} config={fl-256} n={n} nds={[u32(p2, rec+10+j*4) for j in range(min(n,4))]}")
    nxt = None
    for j in range(rec + 10 + 4*n + 8, rec + 500):
        if u32(p2, j) == 0 and u32(p2, j+4) == 0 and 300 <= u16(p2, j+8) <= 500:
            nxt = j; break
    print(f"     nxt={nxt} stride={nxt-rec if nxt else None}")
    if nxt is None: break
    rec = nxt

# --- frame seg7 trace ---
p3 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\frame_assembly.hm")
sh3 = 2033133
for s in range(sh3+16, sh3+48):
    if u32(p3, s) == 0x70241FF5:
        stride = None
        for j in range(s+24, s+250):
            if u32(p3, j) == 0x70241FF5:
                stride = j - s; break
        print(f"\nframe seg7: s={s} stride={stride}")
        for k in range(3):
            rec = s + k*stride
            print(f"  k={k}: CONST={u32(p3,rec)==0x70241FF5} eid={u32(p3,rec+4)} flag16={u32(p3,rec+20)>>16} nds={[u32(p3,rec+24+j*4) for j in range(4)]}")
        break

# --- dummy seg73: locate record via E1392413 rows ---
p4 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\dummy.hm")
hits = [i for i in range(len(p4)-16) if u32(p4,i)==2240 and u32(p4,i+4)==2230 and u32(p4,i+8)==1302 and u32(p4,i+12)==1378]
print("\ndummy E1392413 node hit:", hits)
if hits:
    h = hits[0]
    for k in range(-10, 6):
        off = h + k*4
        print(f"  {k:+3d}: {p4[off:off+4].hex()} u32={u32(p4,off):>10d}")
