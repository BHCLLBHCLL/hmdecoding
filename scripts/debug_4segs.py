
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16

def dump(p, sh, label, nb=72):
    print(f"== {label} seg@{sh} header={[u32(p, sh+j*4) for j in range(6)]}")
    s = sh + 24
    for k in range(0, nb, 4):
        print(f"  +{k:3d}: {p[s+k:s+k+4].hex()} u32={u32(p,s+k):>10d} u16=({u16(p,s+k):>5d},{u16(p,s+k+2):>5d})")

p1 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\frame_assembly.hm")
dump(p1, 2388833, "frame seg12")

p2 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\s_bend_tube.hm")
dump(p2, 367003, "s_bend seg2")

p3 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\yoke.hm")
dump(p3, 8285543, "yoke seg41")

p4 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\dummy.hm")
dump(p4, 258377, "dummy seg73", 88)
# locate E1392432 rows [2232, 2228, 2244, 2246]
hits = [i for i in range(len(p4)-16) if u32(p4,i)==2232 and u32(p4,i+4)==2228 and u32(p4,i+8)==2244 and u32(p4,i+12)==2246]
print("E1392432 node hit:", hits, "rel seg73:", [h-258377 for h in hits])
