
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\body_side.hm")
hdr = 390741
base = hdr + 24
print("u32 stream from +24 (E1..E4 expected nodes [162,167,166,161],[161,166,165,160],[160,165,164,159],[159,164,163,158])")
for k in range(0, 120, 1):
    off = k*4
    print(f"  +{off:4d}: {u32(p, base+off):10d}  0x{u32(p, base+off):08x}")
