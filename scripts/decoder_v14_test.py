
import sys, json, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes

CONST = 0x70241FF5
CONFIG_NODES = {103: 3, 104: 4, 204: 4, 220: 8, 205: 4, 206: 6, 208: 8, 100: 2, 101: 2, 102: 2, 105: 2, 106: 2, 108: 2, 112: 2, 114: 2, 201: 3, 202: 3, 203: 3, 301: 6, 302: 8, 303: 6, 304: 8, 305: 10, 306: 12}

def find_elem_segments(p):
    segs = []
    i = 0
    while i < len(p) - 24:
        if u32(p, i) == 997:
            segid = u32(p, i + 4); cfg71 = u32(p, i + 8); cnt = u32(p, i + 12)
            X = u32(p, i + 16); Y = u32(p, i + 20)
            if X in (2, 3) and 100 <= cfg71 <= 500 and 1 <= cnt <= 10_000_000 and Y < 10_000_000:
                segs.append((i, segid, cfg71, cnt, X, Y))
        i += 1
    return segs

def parse_a_type(p, sh, cnt, row_count, row_map, max_rec=20):
    for s in range(sh + 16, sh + 48):
        if u32(p, s) != CONST:
            continue
        elems = {}
        rec = s
        ok = True
        for k in range(min(cnt, max_rec)):
            if u32(p, rec) != CONST:
                ok = False; break
            eid = u32(p, rec + 4)
            if not (0 < eid < 10_000_000):
                ok = False; break
            nxt = None
            for j in range(rec + 24, min(rec + 200, len(p) - 4)):
                if u32(p, j) == CONST:
                    nxt = j
                    break
            d = (nxt - rec) if nxt else None
            got = None
            prelens = [0, 4, 8, 12] if d else [0]
            for prelen in prelens:
                rec_len = (d - prelen) if d else None
                if rec_len is not None and (rec_len < 32 or rec_len % 4 or rec_len > 140):
                    continue
                lim = (rec_len - 12) if rec_len else 84
                cands = []
                for off in range(12, lim, 4):
                    v = u32(p, rec + off)
                    f = v >> 16
                    if 300 <= f <= 500 and (v & 0xFFFF) == 0:
                        cands.append(off)
                for fp in sorted(cands, reverse=True):
                    nodes_off = rec + fp + 4
                    n = 0
                    while n < 12 and nodes_off + 4 * n + 4 <= len(p) and u32(p, nodes_off + 4 * n) != 0:
                        n += 1
                    if n < 1:
                        continue
                    if rec_len is not None and nodes_off + 4 * n + 8 != rec + rec_len:
                        continue
                    if u32(p, nodes_off + 4 * n) != 0:
                        continue
                    nds = [u32(p, nodes_off + 4 * j) for j in range(n)]
                    if all(1 <= r <= row_count for r in nds):
                        got = (prelen, n, nds, (u32(p, rec + fp) >> 16) - 256)
                        break
                if got:
                    break
            if got is None:
                ok = False; break
            prelen, n, nds, config = got
            elems[eid] = (config, [row_map.get(r, r) for r in nds])
            if nxt is None:
                break
            rec = nxt
        if ok:
            return elems
    return None

def parse_b_type(p, sh, cnt, row_count, row_map, first_eid, max_rec=20):
    s = sh + 24
    elems = {}
    rec = s
    eid = first_eid
    for k in range(min(cnt, max_rec)):
        if u32(p, rec) != 0 or u32(p, rec + 4) != 0:
            return None
        flag = u16(p, rec + 8)
        if not (300 <= flag <= 500):
            return None
        config = flag - 256
        n = CONFIG_NODES.get(config)
        if n is None:
            return None
        nds = [u32(p, rec + 10 + j * 4) for j in range(n)]
        if not all(1 <= r <= row_count for r in nds):
            return None
        elems[eid] = (config, [row_map.get(r, r) for r in nds])
        nxt = None
        for j in range(rec + 10 + 4 * n + 4, rec + 400):
            if u32(p, j) == 0 and u32(p, j + 4) == 0 and 300 <= u16(p, j + 8) <= 500:
                nxt = j
                break
        if nxt is None:
            return None
        stride = nxt - rec
        if u32(p, nxt - 8) != 0:
            return None
        ne = u32(p, nxt - 4)
        if not (0 < ne < 10_000_000):
            return None
        eid = ne
        rec = nxt
    return elems

gt = json.load(open("output/ground_truth/multi_elem_gt.json"))
for fname, info in gt.items():
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{fname}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/{fname}"
    p = load_payload(path)
    ns = find_node_section(p)
    if not ns:
        print(f"== {fname}: NO-NODE"); continue
    hdr, ncount, shift, idoff, coordoff = ns[0]
    nodes, base = parse_nodes(p, hdr, ncount, shift, idoff, coordoff)
    ids = [u32(p, base + k * 52 + idoff) for k in range(ncount)]
    row_map = {k + 1: nid for k, nid in enumerate(ids)}
    segs = find_elem_segments(p)
    elems = {}; notes = []
    for (sh, segid, cfg71, cnt, X, Y) in segs:
        got = parse_a_type(p, sh, cnt, ncount, row_map) if X == 3 else parse_b_type(p, sh, cnt, ncount, row_map, Y)
        if got is None:
            notes.append(f"seg{segid}:fail")
        else:
            elems.update(got)
    matches = 0; total = 0; wrong = []
    for eid_s, d in info["elems"].items():
        eid = int(eid_s); total += 1
        exp = [x for x in d["nodes"] if x]
        if eid in elems and elems[eid][1][:len(exp)] == exp and elems[eid][0] == d["cfg"]:
            matches += 1
        else:
            wrong.append(eid)
    print(f"== {fname}: decoded={len(elems)} match={matches}/{total} notes={notes} wrong={wrong[:3]}")
