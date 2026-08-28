"""v17 SHORT 段取证: dump Y!=2 A 型段的原始字节, 找记录布局."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, is_const

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")

# (sh, segid, cnt, Y) — 来自 v17_gap 诊断
CASES = [
    (31997647, 2000486, 4, 5),
    (44240703, 200043, 19, 9),
    (44267255, 300001, 3, 7),
    (38019435, 6500114, 51, 10),
    (40564251, 100026, 1, 9),
    (44248039, 200045, 1, 5),
]
for sh, segid, cnt, Y in CASES:
    print(f"\n== segid={segid} sh={sh} cnt={cnt} Y={Y}")
    for off in range(0, 160, 4):
        v = u32(p, sh + off)
        note = " CONST" if is_const(v) else ""
        print(f"  {off:+4d}: {p[sh+off:sh+off+4].hex()} u32={v:>10d}{note}")
