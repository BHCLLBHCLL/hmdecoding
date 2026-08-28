"""v17 SHORT 段 CONST 链追踪: 列出段区间内所有 CONST 记录及其解析尝试."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, is_const

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
ROW_COUNT = 354175

CASES = [
    (31997647, 31998339, 2000486, 4),    # Y=5 SHORT, 下一段 sh
    (65235501, 65235501 + 800, 6500115, 6),  # Y=5 OK (最后段)
    (44267255, 44284291, 300001, 3),     # Y=7 SHORT
    (65225749, 65233945, 800029, 73),    # Y=7 OK
    (40564251, 40564463, 100026, 1),     # Y=9 SHORT cnt=1
]
for lo, hi, segid, cnt in CASES:
    print(f"\n== segid={segid} cnt={cnt} region=[{lo},{hi})")
    consts = []
    j = lo + 24
    while True:
        j = p.find(b"\xf5\x1f", j, hi)
        if j < 0:
            break
        if is_const(u32(p, j)):
            consts.append(j)
        j += 1
    print(f"CONST anchors: {len(consts)}")
    for c in consts[:12]:
        eid = u32(p, c + 4)
        # 找 flag: v>>16 in 300..500 low16==0
        flags = []
        for off in range(8, 96, 4):
            v = u32(p, c + off)
            if 300 <= (v >> 16) <= 500 and (v & 0xFFFF) == 0:
                flags.append((off, v >> 16))
        # u16 视图
        print(f"  CONST@{c} eid={eid} flags={flags}")
        for off in range(0, 80, 4):
            v = u32(p, c + off)
            print(f"    +{off:3d}: {p[c+off:c+off+4].hex()} u32={v:>10d}")
        if len(consts) > 3:
            break
