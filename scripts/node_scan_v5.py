
import sys, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

def find_node_section_v5(p, limit=None):
    lim = limit or (len(p) - 100)
    cands = []
    i = 0
    while i < lim - 40:
        if u32(p, i) == 1:
            for gap in range(1, 9):
                j = i + gap * 4
                if j + 24 <= len(p) and u32(p, j) == 136:
                    n = u32(p, j + 4)
                    if 1 <= n <= 10_000_000:
                        cands.append((i, j, n))
        i += 4
    for hi, hj, count in cands[:60]:
        for base in range(hi - 32, hi + 112, 4):
            if base < 0: continue
            for stride in (52, 92, 132):
                ok = 0; bad = 0
                for k in range(min(count, 60)):
                    rec = base + k * stride
                    if rec + stride > len(p):
                        break
                    nid = u32(p, rec + 8)
                    x = d64(p, rec + 20)
                    if 1 <= nid <= 10_000_000 and abs(x) < 1e9:
                        ok += 1
                    else:
                        bad += 1
                        if bad > 4:
                            break
                if ok >= 45 and bad <= 1:
                    return (hi, count, base, stride)
    # structural fallback: scan for 52/92/132 stride streams
    for stride in (52, 92, 132):
        base = 0
        while base + 60 * stride <= len(p):
            ok = 0
            for k in range(30):
                rec = base + k * stride
                if u32(p, rec) == 0 and 1 <= u32(p, rec + 8) <= 10_000_000 and abs(d64(p, rec + 20)) < 1e9:
                    ok += 1
                else:
                    break
            if ok >= 25:
                # count: extend until break
                cnt = ok
                while base + cnt * stride + stride <= len(p):
                    rec = base + cnt * stride
                    if u32(p, rec) == 0 and 1 <= u32(p, rec + 8) <= 10_000_000 and abs(d64(p, rec + 20)) < 1e9:
                        cnt += 1
                    else:
                        break
                return (None, cnt, base, stride)
            base += 4
    return None

for fname in ["molding1.hm", "truck.hm", "car_section.hm", "cover.hm", "SEAT_MODEL.hm"]:
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{fname}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/{fname}"
    p = load_payload(path)
    res = find_node_section_v5(p)
    print(f"== {fname}: {res}")
