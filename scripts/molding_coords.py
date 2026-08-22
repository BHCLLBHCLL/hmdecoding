
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\molding1.hm")
targets = {
    1: (-34.59465, -4.348197, -1e-06),
    2: (-34.530544, -4.618168, -1.495554),
    3: (-34.53051, -4.618293, 1.495834),
    4: (-34.414028, -5.46388, -0.027972),
    5: (-34.326927, -5.392824, -2.617888),
}
for nid, (tx, ty, tz) in targets.items():
    hits = []
    for i in range(0, len(p) - 24):
        x, y, z = d64(p, i), d64(p, i+8), d64(p, i+16)
        if abs(x-tx) < 1e-3 and abs(y-ty) < 1e-3 and abs(z-tz) < 1e-3:
            hits.append(i)
    print(f"N{nid}: coords at {hits[:4]}")
# N1 coords at 210 -> id field? dump around 210-40
s = 210
for off in range(-44, 24, 4):
    print(f"  {off:+4d}: {p[s+off:s+off+4].hex()} u32={int.from_bytes(p[s+off:s+off+4],'little')}")
