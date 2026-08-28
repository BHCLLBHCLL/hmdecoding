"""v17 元素记录布局: dump eid=1 (30170011) 与 eid=100000 (34249971) 周围字节."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, is_const

p = open("output/ground_truth/v17_payload.bin", "rb").read()

for pos, label, rows in [(30170011, "eid=1 rows[94,818,817,820]", [94, 818, 817, 820]),
                          (34249971, "eid=100000 rows[59413,...]", [59413, 60984, 59224, 59236])]:
    print(f"\n== {label} @ {pos}")
    for off in range(-64, 96, 4):
        v = u32(p, pos + off)
        note = " CONST" if is_const(v) else ""
        mark = ""
        # 标记行号出现
        for r in rows:
            if v == r:
                mark = f" <-- row {r}"
        print(f"  {off:+4d}: {p[pos+off:pos+off+4].hex()} u32={v:>10d} u16=({u16(p,pos+off)},{u16(p,pos+off+2)}){note}{mark}")
