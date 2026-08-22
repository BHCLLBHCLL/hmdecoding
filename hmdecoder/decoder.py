#!/usr/bin/env python3
"""hmdecoder — HyperMesh .hm v11.05 容器/节点/单元解码器（差分逆向成果）。"""
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
class HMModel:
    nodes: dict = field(default_factory=dict)
    elements: dict = field(default_factory=dict)
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
    else:
        model.element_variant = "B"
        model.elements = parse_elements_variant_b(p, row_map, ncount)
        model.elem_count = len(model.elements)
    return model

if __name__ == "__main__":
    import sys
    for path in sys.argv[1:]:
        m = decode(path)
        print(f"{path.split('/')[-1]}: db={m.db_version} nodes={len(m.nodes)}/{m.node_count} elems={len(m.elements)}/{m.elem_count} var={m.element_variant}")
