
import sys, json, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32
CONST = 0x70241FF5
MARK = 0x01680000

LAYOUTS = {
    "L48": dict(stride=48, eid_off=4, eid2_off=8, mark_off=24, nodes_off=28, n=4),
    "L76": dict(stride=76, eid_off=32, eid2_off=36, mark_off=48, nodes_off=52, n=4),
}

def find_segments(p):
    segs = []
    i = 0
    while i < len(p) - 16:
        if u32(p, i) == 997:
            cfg = u32(p, i + 8)
            cnt = u32(p, i + 12)
            if 160 <= cfg <= 320 and 1 <= cnt <= 10_000_000:
                segs.append((i, u32(p, i + 4), cfg, cnt))
                i += 16
                continue
        i += 1
    return segs

def try_layout(p, seg, layout, anchors):
    hdr, segid, cfg, cnt = seg
    L = LAYOUTS[layout]
    stride, eid_off, eid2_off, mark_off, nodes_off, n = (L["stride"], L["eid_off"], L["eid2_off"],
                                                         L["mark_off"], L["nodes_off"], L["n"])
    for start in range(hdr + 16, hdr + 80):
        score = 0
        eids = []
        ok_all = True
        probe = min(cnt, 8)
        for k in range(probe):
            rec = start + k * stride
            if rec + stride > len(p): ok_all = False; break
            eid = u32(p, rec + eid_off)
            eid2 = u32(p, rec + eid2_off)
            mark = u32(p, rec + mark_off)
            if eid < 1 or eid2 != (eid << 16 | 2) or mark != MARK:
                ok_all = False; break
            nds = [u32(p, rec + nodes_off + j * 4) for j in range(n)]
            eids.append((eid, nds))
        if not ok_all: continue
        for eid, nds in eids:
            if eid in anchors:
                exp = anchors[eid]["nodes"]
                if nds[:len(exp)] == exp and nds[len(exp):] == [0] * (n - len(exp)):
                    score += 2
                else:
                    score -= 1
        if eids and all(eids[k][0] < eids[k+1][0] for k in range(len(eids)-1)):
            score += 1
        if score >= 0 and (len(eids) < 5 or score > 0):
            return start, layout, eids
    return None

gt = json.load(open("output/ground_truth/multi_elem_gt.json"))
for fname, info in gt.items():
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{fname}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/{fname}"
    p = load_payload(path)
    segs = find_segments(p)
    anchors = info["elems"]
    print(f"== {fname} segs={[(s[1], s[3]) for s in segs]}")
    for seg in segs:
        res = None
        for layout in LAYOUTS:
            res = try_layout(p, seg, layout, anchors)
            if res: break
        if res:
            start, layout, eids = res
            print(f"   seg@{seg[0]} id={seg[1]} cnt={seg[3]} -> {layout} start={start} first={[(e, n[:4]) for e, n in eids[:3]]}")
        else:
            print(f"   seg@{seg[0]} id={seg[1]} cnt={seg[3]} -> UNRESOLVED")
