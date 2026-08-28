"""truck Y=7/Y=4 段结构深挖: 找 CONST 锚 + 记录边界 + 节点行号."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, is_const

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
segs = find_elem_segments(p)

def dump_seg(sh, segid, cnt, X, Y, nrec=6):
    print(f"\n===== seg {segid} Y={Y} cnt={cnt} sh={sh} =====")
    # 找所有 CONST 锚 (在 sh+16 之后, 前 5000 字节内)
    anchors = []
    j = sh + 16
    end = min(sh + 200000, len(p))
    while j < end:
        if is_const(u32(p, j)):
            anchors.append(j)
        j += 4
    print(f"CONST 锚数量 (前 200KB): {len(anchors)}")
    # 打印前 nrec 个锚之间的记录
    for i in range(min(nrec, len(anchors))):
        a = anchors[i]
        b = anchors[i+1] if i+1 < len(anchors) else a + 200
        words = [u32(p, a + 4*k) for k in range(min(16, (b-a)//4))]
        print(f"  rec{i} @{a} len={b-a}: {words}")

for sh, segid, cfg71, cnt, X, Y in segs:
    if Y == 7 and cnt > 100:
        dump_seg(sh, segid, cnt, X, Y)
    if Y == 4 and cnt > 100:
        dump_seg(sh, segid, cnt, X, Y)
