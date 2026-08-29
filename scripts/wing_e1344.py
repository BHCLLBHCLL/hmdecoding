
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm")
# E1344 nodes rows [626, 628, 623, 624]; _parse_a_geom: row @ j+48+4i high16
# search for records with eid=1344 (u32 1344 near @+36) and mark 0x1a040be4
hits = []
for i in range(0, len(p) - 64):
    if u32(p, i) == 0x1a040be4:
        # check eid @+36 = 1344
        if u32(p, i + 36) == 1344:
            hits.append(i)
print("records with eid 1344:", hits[:5])
for h in hits[:2]:
    print(f"--- record @{h} ---")
    for k in range(0, 64, 4):
        print(f"  +{k:3d}: {p[h+k:h+k+4].hex()} u32={u32(p,h+k):>10d} u16=({u16(p,h+k):>5d},{u16(p,h+k+2):>5d})")
    # nodes rows
    rows = [u32(p, h + 48 + 4*i) >> 16 for i in range(4)]
    print("  rows:", rows)
