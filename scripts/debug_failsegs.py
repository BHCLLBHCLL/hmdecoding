
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\frame_assembly.hm")
for sh in (2033133, 2388833):
    print(f"== frame seg@{sh} header={[u32(p, sh+j*4) for j in range(6)]}")
    s = sh + 24
    for k in range(0, 56, 4):
        print(f"  +{k:3d}: {p[s+k:s+k+4].hex()} u32={u32(p,s+k):>9d} u16=({u16(p,s+k):>4d},{u16(p,s+k+2):>4d})")

p2 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\head_2.hm")
sh2 = 100870
print(f"\n== head_2 seg2@{sh2} header={[u32(p2, sh2+j*4) for j in range(6)]}")
s2 = sh2 + 24
for k in range(0, 56, 4):
    print(f"  +{k:3d}: {p2[s2+k:s2+k+4].hex()} u32={u32(p2,s2+k):>9d} u16=({u16(p2,s2+k):>4d},{u16(p2,s2+k+2):>4d})")

p3 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\s_bend_tube.hm")
sh3 = 367003
print(f"\n== s_bend seg2@{sh3} header={[u32(p3, sh3+j*4) for j in range(6)]}")
s3 = sh3 + 24
for k in range(0, 56, 4):
    print(f"  +{k:3d}: {p3[s3+k:s3+k+4].hex()} u32={u32(p3,s3+k):>9d} u16=({u16(p3,s3+k):>4d},{u16(p3,s3+k+2):>4d})")
