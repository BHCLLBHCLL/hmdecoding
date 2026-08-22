
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\bottle.hm")
seg = 45421
print(f"seg@45421 (mod4={seg%4})")
print("header bytes:")
for k in range(0, 28, 4):
    print(f"  {seg+k}: {p[seg+k:seg+k+4].hex()}")
# record stream from seg+24 (assuming 24B header)
s = seg + 24
print(f"record stream from {s} (mod4={s%4}), 60 bytes:")
for k in range(0, 60, 4):
    b = p[s+k:s+k+4]
    print(f"  {s+k} ({k:+4d}): {b.hex()}  u32={u32(p, s+k)} u16pair=({u16(p,s+k)},{u16(p,s+k+2)})")
# anchor positions: E4442 nodes [105,468,465,739] at 45455
print(f"\nE4442 node area @45455: {[u32(p, 45455+j*4) for j in range(4)]}")
print(f"E4441 node area @45489: {[u32(p, 45489+j*4) for j in range(4)]}")
print(f"E4440 node area @45523: {[u32(p, 45523+j*4) for j in range(4)]}")
# dump raw bytes between 45445 and 45530
print("\nraw bytes 45445..45545:")
print(p[45445:45545].hex(" "))
