"""诊断 shell_section.hm 元素段 @917."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, is_const, find_elem_segments

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\shell_section.hm", "rb").read()
p = gzip.decompress(raw[12:])
print(f"payload {len(p)}")

segs = find_elem_segments(p)
print("elem segs:", segs)
for sh, segid, cfg71, cnt, X, Y in segs:
    print(f"\n== seg @{sh} segid={segid} cfg71={cfg71} cnt={cnt} X={X} Y={Y}")
    for off in range(0, 96, 4):
        q = sh + off
        if q + 4 > len(p):
            break
        v = u32(p, q)
        mark = " <CONST>" if is_const(v) else ""
        print(f"  +{off:3d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)}){mark}")
