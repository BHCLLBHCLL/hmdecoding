"""v17 OK vs SHORT 特殊段对比: dump 相邻段找差异."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, is_const

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")

CASES = [
    (38005415, 6500113, 125, 7, "OK"),
    (38019435, 6500114, 51, 10, "SHORT"),
    (65235501, 6500115, 6, 5, "OK"),
    (65219823, 800026, 6, 4, "SHORT"),
    (65220593, 800027, 41, 6, "SHORT"),
    (65225749, 800029, 73, 7, "OK"),
    (65233945, 800030, 12, 8, "SHORT"),
]
for sh, segid, cnt, Y, st in CASES:
    print(f"\n== segid={segid} sh={sh} cnt={cnt} Y={Y} {st}")
    # 段头 + 第一条记录前 96B (从 CONST 起)
    for off in range(0, 128, 4):
        v = u32(p, sh + off)
        note = " CONST" if is_const(v) else ""
        # u16 视图 (槽位布局线索)
        lo, hi = u16(p, sh + off), u16(p, sh + off + 2)
        print(f"  {off:+4d}: {p[sh+off:sh+off+4].hex()} u32={v:>10d} u16=({lo},{hi}){note}")
