
import sys, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

def dump(p, sh, label, nb=64):
    print(f"== {label} seg@{sh} header={[u32(p, sh+j*4) for j in range(6)]}")
    s = sh + 24
    for k in range(0, nb, 4):
        print(f"  +{k:3d}: {p[s+k:s+k+4].hex()} u32={u32(p,s+k):>9d} u16=({u16(p,s+k):>5d},{u16(p,s+k+2):>5d})")

p1 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\c_channel-tcl.hm")
import struct
print("db:", struct.unpack_from("<d", p1, 4)[0])
sh = [i for i in range(len(p1)-24) if u32(p1,i)==997][0]
dump(p1, sh, "c_channel-tcl")

p2 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\composites.hm")
sh = [i for i in range(len(p2)-24) if u32(p2,i)==997][0]
dump(p2, sh, "composites", 48)

p3 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\joints.hm")
sh = [i for i in range(len(p3)-24) if u32(p3,i)==997][0]
dump(p3, sh, "joints", 48)
