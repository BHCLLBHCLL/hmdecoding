"""复现 _parse_a_type 的 family-1 检测, 统计 SEAT_MODEL 失败原因."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, is_const

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_count = len(n1)
segs = find_elem_segments(p)

ok = fail_flag = fail_rows = 0
for sh, segid, cfg71, cnt, X, Y in segs:
    rec = sh + 24
    for k in range(cnt):
        if not is_const(u32(p, rec)):
            break
        f1_eid = u16(p, rec + 18) | (u16(p, rec + 20) << 16)
        if (u32(p, rec + 8) in (0x02BD0002, 0x02AE0002)
                and u16(p, rec + 12) == 2596
                and u32(p, rec + 4) != f1_eid):
            f1_flag = u32(p, rec + 28)
            if not (300 <= (f1_flag >> 16) <= 500 and (f1_flag & 0xFFFF) == 0):
                fail_flag += 1
            else:
                rows = []
                kk = rec + 32
                while len(rows) < 12 and u32(p, kk) != 0:
                    rows.append(u32(p, kk)); kk += 4
                if not (1 <= len(rows) <= 12 and all(1 <= r <= row_count for r in rows)):
                    fail_rows += 1
                else:
                    ok += 1
        j = p.find(b"\xf5\x1f\x24\x70", rec + 44, rec + 300)
        if j < 0:
            break
        rec = j
print(f"family-1: ok={ok} fail_flag={fail_flag} fail_rows={fail_rows}")
