
import sys, json, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes

CONST = 0x70241FF5

def find_elem_segments(p):
    segs = []
    i = 0
    while i < len(p) - 24:
        if u32(p, i) == 997:
            segid = u32(p, i + 4); cfg71 = u32(p, i + 8); cnt = u32(p, i + 12)
            X = u32(p, i + 16); Y = u32(p, i + 20)
            if X in (2, 3) and 100 <= cfg71 <= 500 and 1 <= cnt <= 10_000_000 and Y < 10_000_000 and segid < 1_000_000:
                segs.append((i, segid, cfg71, cnt, X, Y))
        i += 1
    return segs

def parse_a_type(p, s, cnt, row_count, row_map, config, maxprobe=200):
    stride = None
    for j in range(s + 24, min(s + 24 + maxprobe, len(p) - 4)):
        if u32(p, j) == CONST:
            stride = j - s
            break
    if stride is None or stride % 4:
        return None, "no-const-stride"
    target = (config + 256) << 16
    fp = None
    for off in range(12, stride - 12, 4):
        if u32(p, s + off) == target:
            fp = off
            break
    if fp is None:
        return None, f"no-flag@{config}"
    nodes_off = fp + 4
    if (stride - nodes_off - 8) % 4 or stride - nodes_off < 12:
        return None, "bad-len"
    n = (stride - nodes_off - 8) // 4
    if not (1 <= n <= 12):
        return None, f"bad-n={n}"
    elems = {}
    for k in range(min(cnt, 10)):
        rec = s + k * stride
        if u32(p, rec) != CONST or u32(p, rec + fp) != target:
            return None, f"rec{k}-mismatch"
        eid = u32(p, rec + 4)
        if not (0 < eid < 10_000_000):
            return None, f"bad-eid={eid}"
        nds = [u32(p, rec + nodes_off + j * 4) for j in range(n)]
        if not all(1 <= r <= row_count for r in nds):
            return None, f"rec{k}-badrow={nds}"
        elems[eid] = (config, [row_map.get(r, r) for r in nds])
    return elems, "ok"

def parse_b_type(p, s, cnt, row_count, row_map, config, first_eid, maxprobe=300):
    stride = None
    for j in range(s + 22, min(s + 22 + maxprobe, len(p) - 4)):
        if u32(p, j) == 0 and u32(p, j + 4) == 0 and u16(p, j + 8) == config + 256:
            stride = j - s
            break
    if stride is None:
        return None, "no-next-rec"
    n = (stride - 18) // 4
    if not (1 <= n <= 12) or 18 + 4 * n != stride:
        return None, f"bad-stride={stride}"
    elems = {}
    for k in range(min(cnt, 10)):
        rec = s + k * stride
        if u32(p, rec) != 0 or u32(p, rec + 4) != 0 or u16(p, rec + 8) != config + 256:
            return None, f"rec{k}-mismatch"
        nds = [u32(p, rec + 10 + j * 4) for j in range(n)]
        if not all(1 <= r <= row_count for r in nds):
            return None, f"rec{k}-badrow={nds}"
        eid = first_eid - k
        if eid < 1:
            return None, f"eid<1@{k}"
        elems[eid] = (config, [row_map.get(r, r) for r in nds])
    return elems, "ok"

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
        config = cfg71 - 71
        if X == 3:
            got, why = parse_a_type(p, sh + 24, cnt, ncount, row_map, config)
        else:
            got, why = parse_b_type(p, sh + 24, cnt, ncount, row_map, config, Y)
        if got is None:
            notes.append(f"seg{segid}:{why}")
        else:
            elems.update(got)
    matches = 0; total = 0
    for eid, d in info["elems"].items():
        total += 1
        exp = [x for x in d["nodes"] if x]
        if eid in elems and elems[eid][1][:len(exp)] == exp and elems[eid][0] == d["cfg"]:
            matches += 1
    print(f"== {fname}: decoded={len(elems)} match={matches}/{total} notes={notes}")
