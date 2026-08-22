
import sys, json, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section, parse_nodes

CONST = 0x70241FF5

def find_elem_segments(p):
    segs = []
    i = 0
    while i < len(p) - 24:
        if u32(p, i) == 997:
            segid = u32(p, i + 4)
            cfg71 = u32(p, i + 8)
            cnt = u32(p, i + 12)
            X = u32(p, i + 16)
            Y = u32(p, i + 20)
            if X in (2, 3) and 100 <= cfg71 <= 500 and 1 <= cnt <= 10_000_000 and Y < 10_000_000 and segid < 1_000_000:
                segs.append((i, segid, cfg71, cnt, X, Y))
        i += 1
    return segs

def find_next_const(p, s, lo, hi):
    for j in range(s + lo, min(s + hi, len(p) - 4)):
        if u32(p, j) == CONST:
            return j
    return None

def parse_a_type(p, s, cnt, row_count, row_map, config):
    """Find stride via CONST chain; locate flag<<16; extract nodes."""
    stride = find_next_const(p, s, 24, 140)
    if stride is None:
        return None
    stride -= s
    if stride % 4:
        return None
    elems = {}
    for k in range(min(cnt, 8)):
        rec = s + k * stride
        if u32(p, rec) != CONST:
            return None
        eid = u32(p, rec + 4)
        if not (0 < eid < 10_000_000):
            return None
        if k and eid <= last_eid:
            return None
        last_eid = eid
    # find flag<<16 within first record
    fp = None
    target = (config + 256) << 16
    for off in range(12, stride - 12, 4):
        if u32(p, s + off) == target:
            fp = off
            break
    if fp is None:
        return None
    nodes_off = fp + 4
    tail_len = stride - nodes_off - 4 * 2  # [0][tail]
    n = tail_len // 4
    if not (1 <= n <= 12) or nodes_off + 4 * n + 8 != stride:
        return None
    for k in range(min(cnt, 8)):
        rec = s + k * stride
        nds = [u32(p, rec + nodes_off + j * 4) for j in range(n)]
        if not all(1 <= r <= row_count for r in nds):
            return None
        eid = u32(p, rec + 4)
        elems[eid] = (config, [row_map.get(r, r) for r in nds])
    return elems

def parse_b_type(p, s, cnt, row_count, row_map, config, first_eid):
    """Find next record start; nodes at +10; eid descending from first_eid."""
    stride = None
    for j in range(s + 24, min(s + 200, len(p) - 4)):
        if u32(p, j) == 0 and u32(p, j + 4) == 0 and u16(p, j + 8) == config + 256:
            stride = j - s
            break
    if stride is None or stride % 4:
        return None
    n = (stride - 18) // 4
    if not (1 <= n <= 12) or 18 + 4 * n != stride:
        return None
    elems = {}
    for k in range(min(cnt, 8)):
        rec = s + k * stride
        if u32(p, rec) != 0 or u32(p, rec + 4) != 0 or u16(p, rec + 8) != config + 256:
            return None
        nds = [u32(p, rec + 10 + j * 4) for j in range(n)]
        if not all(1 <= r <= row_count for r in nds):
            return None
        eid = first_eid - k
        if eid < 1:
            return None
        elems[eid] = (config, [row_map.get(r, r) for r in nds])
    return elems

gt = json.load(open("output/ground_truth/multi_elem_gt.json"))
results = {}
for fname, info in gt.items():
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{fname}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/{fname}"
    p = load_payload(path)
    ns = find_node_section(p)
    if not ns:
        print(f"== {fname}: no node section"); continue
    hdr, ncount, shift, idoff, coordoff = ns[0]
    nodes, base = parse_nodes(p, hdr, ncount, shift, idoff, coordoff)
    ids = [u32(p, base + k * 52 + idoff) for k in range(ncount)]
    row_map = {k + 1: nid for k, nid in enumerate(ids)}
    segs = find_elem_segments(p)
    elems = {}
    notes = []
    for (sh, segid, cfg71, cnt, X, Y) in segs:
        config = cfg71 - 71
        s = sh + 24
        got = None
        if X == 3:
            got = parse_a_type(p, s, cnt, ncount, row_map, config)
            if got is None:
                notes.append(f"seg{segid} A-fail")
        else:
            got = parse_b_type(p, s, cnt, ncount, row_map, config, Y)
            if got is None:
                notes.append(f"seg{segid} B-fail")
        if got:
            elems.update(got)
    # match oracle anchors
    matches = 0; total = 0; wrong = []
    for eid, d in info["elems"].items():
        total += 1
        if eid in elems and elems[eid][1][:len(d["nodes"])] == [x for x in d["nodes"] if x] and elems[eid][0] == d["cfg"]:
            matches += 1
        else:
            wrong.append(eid)
    print(f"== {fname}: segs={len(segs)} decoded={len(elems)} anchor-match={matches}/{total} {notes} wrong={wrong[:3]}")
    results[fname] = matches
