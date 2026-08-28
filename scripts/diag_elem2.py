"""dump shell_section.hm 全部 8 条 A 型记录."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\shell_section.hm", "rb").read()
p = gzip.decompress(raw[12:])

for sh in (917, 1153):
    # 记录从 +24 起, 间距 36
    cnt = 6 if sh == 917 else 2
    print(f"\n== seg @{sh} ({cnt} recs) ==")
    for k in range(cnt):
        rec = sh + 24 + k * 36
        print(f" rec{k} @{rec}:")
        for off in range(0, 36, 4):
            q = rec + off
            v = u32(p, q)
            print(f"   +{off:2d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)})")
