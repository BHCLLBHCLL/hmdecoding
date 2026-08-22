#!/usr/bin/env python3
"""hmdecoder — HyperMesh .hm v11.05 容器/节点/单元/显示/几何点解码器。"""
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
MARK_GEOM = 0x40008126

def find_node_section(p):
    cands = []
    for i in range(0, len(p) - 28):
        if u32(p, i + 8) == 1 and u32(p, i + 12) == 136:
            n = u32(p, i + 16)
            if 1 <= n <= 10_000_000:
                cands.append((i, n))
    best = None
    for hdr, count in cands[:8]:
        for shift, idoff, coordoff in ((20, 0, 0xC), (24, 0, 0xC), (20, 4, 0x10), (16, 0, 0xC)):
            base = hdr + shift
            ok = 0; bad = 0; total = 0
            probe = min(count, 200)
            for k in range(probe):
                rec = base + k * 52
                if rec + 0x30 > len(p):
                    break
                nid = u32(p, rec + idoff)
                x = d64(p, rec + coordoff); y = d64(p, rec + coordoff + 8); z = d64(p, rec + coordoff + 16)
                total += 1
                if 1 <= nid <= 10_000_000 and abs(x) < 1e9 and abs(y) < 1e9 and abs(z) < 1e9:
                    ok += 1
                else:
                    bad += 1
                    if bad > 40 and count > 100:
                        break
            need = max(3, min(count // 4, 150))
            if total >= need and ok >= need and ok > bad * 4:
                cfg = (ok, hdr, count, shift, idoff, coordoff)
                if best is None or ok > best[0]:
                    best = cfg
    if best:
        return [best[1:]]
    return []

def parse_nodes(p, hdr, count, shift, idoff, coordoff):
    nodes = {}
    base = hdr + shift
    for k in range(count):
        rec = base + k * 52
        if rec + 0x30 > len(p):
            break
        nid = u32(p, rec + idoff)
        x = d64(p, rec + coordoff); y = d64(p, rec + coordoff + 8); z = d64(p, rec + coordoff + 16)
        nodes[nid] = Node(nid, x, y, z)
    return nodes, base

def find_elem_header(p):
    for i in range(0, len(p) - 16):
        if u32(p, i) == 997 and u32(p, i + 4) == 3 and u32(p, i + 8) == 175:
            n = u32(p, i + 12)
            if 1 <= n <= 100_000_000:
                return (i, n)
    return None

def parse_elements_variant_a(p, row_map):
    elems = {}
    for i in range(0, len(p) - 0x30):
        if u32(p, i) == 0 and u32(p, i + 4) == 0x01680000:
            refs = [u32(p, i + 8 + j * 4) for j in range(4)]
            eid = u32(p, i + 0x24) - 1
            if eid < 1 or all(r == 0 for r in refs):
                continue
            nodes = [row_map.get(r, r) for r in refs if r != 0]
            if eid not in elems:
                elems[eid] = Elem(eid, nodes, 0)
    for i in range(0x20, len(p) - 0x30):
        if u32(p, i + 0x20) == CONST and u32(p, i + 0x28) == 0x10019:
            refs = [u32(p, i + j * 4) for j in range(4)]
            nodes = [row_map.get(r, r) for r in refs if r != 0]
            if nodes:
                eid = max(elems) + 1 if elems else 1
                if eid not in elems:
                    elems[eid] = Elem(eid, nodes, 0)
    return elems

def parse_elements_variant_b(p, row_map, row_count):
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
    """变体 B 几何点 v4: [id][1] 块 + 5 偏移候选 + 评分（z 整数 + 52B 家族必选 + y 参数过滤）。"""
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
                        for d in (52, -52, 104, -104):
                            j2 = j + d
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

def decode(path):
    p = load_payload(path)
    model = HMModel(db_version=d64(p, 4))
    ns = find_node_section(p)
    if not ns:
        return model
    hdr, ncount, shift, idoff, coordoff = ns[0]
    model.node_count = ncount
    model.node_section = hdr
    nodes, base = parse_nodes(p, hdr, ncount, shift, idoff, coordoff)
    model.nodes = nodes
    if not nodes:
        return model
    row_order = [u32(p, base + k * 52 + idoff) for k in range(ncount)]
    row_map = {k + 1: nid for k, nid in enumerate(row_order)}
    ehdr = find_elem_header(p)
    if ehdr:
        model.elem_section = ehdr[0]
        model.elem_count = ehdr[1]
        model.element_variant = "A"
        model.elements = parse_elements_variant_a(p, row_map)
        model.display_points = parse_display_points(p)
    else:
        model.element_variant = "B"
        model.elements = parse_elements_variant_b(p, row_map, ncount)
        model.elem_count = len(model.elements)
        model.geo_points = parse_geo_points_variant_b(p, set(model.nodes))
    return model

if __name__ == "__main__":
    import sys
    for path in sys.argv[1:]:
        m = decode(path)
        print(f"{path.split('/')[-1]}: db={m.db_version} nodes={len(m.nodes)}/{m.node_count} elems={len(m.elements)}/{m.elem_count} display={len(m.display_points)} geopts={len(m.geo_points)} var={m.element_variant}")
