#!/usr/bin/env python3
"""hmdecoder — HyperMesh .hm 容器/节点/单元/显示/几何点解码器。

支持 DB 版本族: v10-legacy, v11-classic (11.03–11.05), v12-13 (部分).
节点段: [136] 头 + 记录 52B ([id][0][0][x][y][z][0x4]) / 92B (+40B 附加) / 56B ([x][y][z][0x4][id+1][0][0]).
元素段: [997][seg][175][count][X][Y]; A 型 (X=3, CONST 锚) / B 型 (X=2, 链式 eid).
"""
import gzip, struct
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class Node:
    id: int
    x: float; y: float; z: float

@dataclass
class Elem:
    id: int
    nodes: list
    config: int = 0

@dataclass
class DisplayPoint:
    id: int
    x: float; y: float; z: float

@dataclass
class GeoPoint:
    id: int
    x: float; y: float; z: float

@dataclass
class HMModel:
    nodes: dict = field(default_factory=dict)
    elements: dict = field(default_factory=dict)
    display_points: dict = field(default_factory=dict)
    geo_points: dict = field(default_factory=dict)
    db_version: float = 0.0
    node_count: int = 0
    elem_count: int = 0
    node_section: int = 0
    elem_section: int = 0
    element_variant: str = ""

def load_payload(path):
    raw = Path(path).read_bytes()
    assert raw[:4] == b"\x00\x00\x00\x00", "非标准前缀"
    ver = struct.unpack_from("<d", raw, 4)[0]
    assert abs(ver - 5.0) < 1e-9, f"包装版本异常: {ver}"
    return gzip.decompress(raw[12:])

def u32(p, o): return struct.unpack_from("<I", p, o)[0]
def u16(p, o): return struct.unpack_from("<H", p, o)[0]
def d64(p, o): return struct.unpack_from("<d", p, o)[0]
CONST = 0x70241FF5
CONST_12 = 0x70501FF5  # v12-13 元素段常量
MARK_GEOM = 0x40008126

def is_const(v):
    """元素段常量家族: 0x70??1FF5 (v11: 0x70241FF5, v12-13: 0x70501FF5)."""
    return (v & 0xFFFF) == 0x1FF5 and ((v >> 24) & 0xFF) == 0x70

NODE_LAYOUTS = ((52, 0, 12, False), (52, 4, 12, False), (52, 8, 20, False),
                (92, 0, 12, False), (92, 4, 12, False), (92, 8, 20, False),
                (56, 44, 0, True))

def find_node_section(p):
    hits = []
    start = 0
    while True:
        i = p.find(b"\x88\x00\x00\x00", start)
        if i < 0:
            break
        n = u32(p, i + 4)
        if 1 <= n <= 10_000_000:
            hits.append((i, n))
        start = i + 1
    hits.sort(key=lambda h: -h[1])
    best = None
    for hi, count in hits[:600]:
        for base in range(hi - 32, hi + 48, 4):
            if base < 0:
                continue
            for stride, idoff, xoff, chain in NODE_LAYOUTS:
                ok = 0; bad = 0
                seen = set()
                for k in range(min(count, 60)):
                    rec = base + k * stride
                    if rec + stride > len(p):
                        break
                    x = d64(p, rec + xoff)
                    if chain:
                        tailok = u32(p, rec + 48) == 0 and u32(p, rec + 52) == 0
                        nid = u32(p, rec + 44) - 1
                    else:
                        tailok = True
                        nid = u32(p, rec + idoff)
                    if 1 <= nid <= 10_000_000 and abs(x) < 1e9 and tailok:
                        ok += 1
                        seen.add(nid)
                    else:
                        bad += 1
                        if bad > 3:
                            break
                # 假候选 id 大量重复 (如 molding1 base=142 全 3) -> 淘汰
                if len(seen) < max(5, ok // 2):
                    continue
                if ok > 30 and (best is None or ok > best[0]):
                    best = (ok, (hi, count, base, stride, idoff, chain))
    if best and best[0] >= 45:
        return best[1]
    return None

def parse_nodes(p, cfg):
    hi, count, base, stride, idoff, chain = cfg
    nodes = {}
    for k in range(count):
        rec = base + k * stride
        if rec + stride > len(p):
            break
        if chain:
            nid = u32(p, rec + 44) - 1
            x, y, z = d64(p, rec), d64(p, rec + 8), d64(p, rec + 16)
        else:
            nid = u32(p, rec + idoff)
            x, y, z = d64(p, rec + 12), d64(p, rec + 20), d64(p, rec + 28)
        if not (1 <= nid <= 10_000_000) or not (abs(x) < 1e9 and abs(y) < 1e9 and abs(z) < 1e9):
            break  # 记录流结束 (count 字段可能含虚值)
        nodes[nid] = Node(nid, x, y, z)
    return nodes, base

def row_map_from_nodes(p, cfg, base):
    hi, count, stride, idoff, chain = cfg[0], cfg[1], cfg[3], cfg[4], cfg[5]
    if chain:
        return {k + 1: k + 1 for k in range(count)}
    return {k + 1: u32(p, base + k * stride + idoff) for k in range(count)}

# ---------------------------------------------------------------------------
# 元素段
# ---------------------------------------------------------------------------
CONFIG_NODES = {103: 3, 104: 4, 204: 4, 220: 8, 205: 4, 206: 6, 208: 8,
                100: 2, 101: 2, 102: 2, 105: 2, 106: 2, 108: 2, 112: 2, 114: 2,
                201: 3, 202: 3, 203: 3, 301: 6, 302: 8, 303: 6, 304: 8, 305: 10, 306: 12}

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

def _parse_a_type(p, sh, cnt, row_count, row_map, max_rec=None):
    for s in range(sh + 16, sh + 64):
        if not is_const(u32(p, s)):
            continue
        elems = {}
        rec = s
        ok = True
        for k in range(min(cnt, max_rec if max_rec else cnt)):
            if not is_const(u32(p, rec)):
                # 断点重连: 记录流可能被其他数据块打断
                nxt = None
                for j in range(rec + 4, min(rec + 200, len(p) - 4)):
                    if is_const(u32(p, j)):
                        nxt = j
                        break
                if nxt is None:
                    ok = False; break
                rec = nxt
                if not is_const(u32(p, rec)):
                    ok = False; break
            eid = u32(p, rec + 4)
            if not (0 < eid < 10_000_000):
                ok = False; break
            nxt = None
            for j in range(rec + 24, min(rec + 200, len(p) - 4)):
                if is_const(u32(p, j)):
                    nxt = j
                    break
            d = (nxt - rec) if nxt else None
            got = None
            # ---- v11 路径: flag<<16 u32 + u32 节点 ----
            prelens = [0, 4, 8, 12, 16, 20, 24, 28, 32] if d else [0]
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
            # ---- v12 路径: u16 flag + u16 槽位节点 (58B 记录等) ----
            if got is None:
                for fp in range(16, 56, 2):
                    f = u16(p, rec + fp)
                    if not (300 <= f <= 500):
                        continue
                    nodes_off = rec + fp + 2
                    n = 0
                    while n < 12 and u16(p, nodes_off + 4 * n) != 0 and u16(p, nodes_off + 4 * n + 2) == 0:
                        n += 1
                    if n < 1:
                        continue
                    nds = [u16(p, nodes_off + 4 * j) for j in range(n)]
                    if all(1 <= r <= row_count for r in nds):
                        got = (fp, n, nds, f - 256)
                        break
            if got is None:
                ok = False; break
            fp, n, nds, config = got
            elems[eid] = (config, [row_map.get(r, r) for r in nds])
            if nxt is None:
                break
            rec = nxt
        if ok:
            return elems
    return None

def _parse_b_type(p, sh, cnt, row_count, row_map, first_eid, max_rec=None):
    s = sh + 24
    elems = {}
    rec = s
    eid = first_eid
    for k in range(min(cnt, max_rec if max_rec else cnt)):
        if u32(p, rec) != 0 or u32(p, rec + 4) != 0:
            # 断点重连: 跳过异常数据块继续
            nxt = None
            for j in range(rec + 4, min(rec + 400, len(p) - 4)):
                if u32(p, j) == 0 and u32(p, j + 4) == 0 and 300 <= u16(p, j + 8) <= 500:
                    nxt = j
                    break
            if nxt is None:
                break
            rec = nxt
            if u32(p, rec) != 0 or u32(p, rec + 4) != 0:
                break
        flag = u16(p, rec + 8)
        if not (300 <= flag <= 500):
            break
        config = flag - 256
        n = CONFIG_NODES.get(config)
        if n is None:
            break
        nds = [u32(p, rec + 10 + j * 4) for j in range(n)]
        if not all(1 <= r <= row_count for r in nds):
            break
        elems[eid] = (config, [row_map.get(r, r) for r in nds])
        nxt = None
        for j in range(rec + 10 + 4 * n + 4, rec + 400):
            if u32(p, j) == 0 and u32(p, j + 4) == 0 and 300 <= u16(p, j + 8) <= 500:
                nxt = j
                break
        if nxt is None:
            break
        stride = nxt - rec
        if u32(p, nxt - 8) != 0:
            break
        ne = u32(p, nxt - 4)
        if not (0 < ne < 10_000_000):
            break
        eid = ne
        rec = nxt
    return elems

def decode_elements(p, row_map, row_count):
    segs = find_elem_segments(p)
    if not segs:
        return None
    elems = {}
    for (sh, segid, cfg71, cnt, X, Y) in segs:
        got = _parse_a_type(p, sh, cnt, row_count, row_map) if X == 3 else _parse_b_type(p, sh, cnt, row_count, row_map, Y)
        if got:
            elems.update(got)
    return elems or None

# ---------------------------------------------------------------------------
# 显示点 / 几何点
# ---------------------------------------------------------------------------
def parse_display_points(p):
    points = {}
    marks = [i for i in range(len(p) - 8) if u32(p, i) == MARK_GEOM]
    for m in marks:
        off = u32(p, m + 4)
        if off >= len(p):
            continue
        best = None
        for start in range(off, min(off + 0x40, len(p) - 52)):
            ok = True
            for k in range(10):
                rec = start + k * 52
                if rec + 52 > len(p):
                    ok = False; break
                x, y, z = d64(p, rec), d64(p, rec + 8), d64(p, rec + 16)
                if not (abs(x) < 1e6 and abs(y) < 1e6 and abs(z) < 1e6):
                    ok = False; break
            if not ok:
                continue
            score = sum(1 for k in range(10) if 0 < u32(p, start + k * 52 + 40) < 1e6)
            if best is None or score > best[0]:
                best = (score, start)
        if not best or best[0] < 3:
            continue
        base = best[1]
        k = 0
        while base + 52 <= len(p) and k < 200000:
            rec = base + k * 52
            x, y, z = d64(p, rec), d64(p, rec + 8), d64(p, rec + 16)
            rid = u32(p, rec + 40)
            if not (abs(x) < 1e6 and abs(y) < 1e6 and abs(z) < 1e6):
                break
            if 0 < rid < 1e6:
                points[rid] = DisplayPoint(rid, x, y, z)
            k += 1
    return points

def parse_geo_points_variant_b(p, node_ids=None):
    OFFSETS = (-249, -145, -93, -41, 15)
    n = len(p)
    results = {}
    i = 0
    while i < n - 8:
        v = u32(p, i)
        if 1 <= v <= 10_000_000 and u32(p, i + 4) == 1 and v not in results and (not node_ids or v not in node_ids):
            best = None
            for off in OFFSETS:
                j = i + off
                if 0 <= j and j + 24 <= n:
                    x, y, z = d64(p, j), d64(p, j + 8), d64(p, j + 16)
                    if abs(x) < 1e5 and abs(y) < 1e5 and abs(z) < 1e5 and abs(x) > 1 and abs(y) > 1:
                        if abs(y - 2.063) < 1e-3:
                            continue
                        s = 0
                        if abs(z - round(z)) < 1e-4:
                            s += 10
                        for dd in (52, -52, 104, -104):
                            j2 = j + dd
                            if 0 <= j2 and j2 + 24 <= n:
                                x2, y2, z2 = d64(p, j2), d64(p, j2 + 8), d64(p, j2 + 16)
                                if abs(x2 - x) < 1e-4 and abs(y2 - y) < 1e-4 and abs(z2 - z) < 1e-4:
                                    s += 20
                                    break
                        if best is None or s > best[0]:
                            best = (s, j, x, y, z)
            if best and best[0] >= 20:
                results[v] = GeoPoint(v, best[2], best[3], best[4])
            i += 8
        else:
            i += 1
    return results

# ---------------------------------------------------------------------------
def decode(path):
    p = load_payload(path)
    model = HMModel(db_version=d64(p, 4))
    ns = find_node_section(p)
    if ns:
        model.node_section = ns[0]
        model.node_count = ns[1]
        nodes, base = parse_nodes(p, ns)
        model.nodes = nodes
        if nodes:
            row_map = row_map_from_nodes(p, ns, base)
            elems = decode_elements(p, row_map, ns[1])
            elems_b = _parse_ws_variant_b(p, row_map, ns[1])
            if elems_b and (not elems or len(elems_b) > len(elems)):
                model.elements = elems_b
                model.elem_count = len(elems_b)
                model.element_variant = "WS-B"
            elif elems:
                model.elements = elems
                model.elem_count = len(elems)
                model.element_variant = "segmented"
            model.display_points = parse_display_points(p)
            if not model.elements:
                model.geo_points = parse_geo_points_variant_b(p, set(model.nodes))
    return model

def _parse_ws_variant_b(p, row_map, row_count):
    elems = {}
    for i in range(0, len(p) - 30):
        if u32(p, i + 4) == 0 and u32(p, i + 8) == 0:
            eid = u32(p, i)
            flag = u16(p, i + 12)
            if eid < 100000 or eid > 10_000_000 or flag not in (359, 460):
                continue
            refs = [u16(p, i + 14), u16(p, i + 18), u16(p, i + 22), u16(p, i + 26)]
            if not all(r <= row_count for r in refs):
                continue
            nodes = [row_map.get(r, 0) for r in refs if r != 0]
            if eid not in elems:
                elems[eid] = Elem(eid, nodes, flag - 256)
    return elems

if __name__ == "__main__":
    import sys
    for path in sys.argv[1:]:
        m = decode(path)
        print(f"{path.split('/')[-1]}: db={m.db_version} nodes={len(m.nodes)}/{m.node_count} "
              f"elems={len(m.elements)}/{m.elem_count} display={len(m.display_points)} "
              f"geopts={len(m.geo_points)} var={m.element_variant}")