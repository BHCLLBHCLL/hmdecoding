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

@dataclass
class HMModel:
    nodes: dict = field(default_factory=dict)
    elements: dict = field(default_factory=dict)
    db_version: float = 0.0
    node_count: int = 0
    elem_count: int = 0
    node_section: int = 0
    elem_section: int = 0

def load_payload(path):
    raw = Path(path).read_bytes()
    assert raw[:4] == b"\x00\x00\x00\x00", "非标准前缀"
    ver = struct.unpack_from("<d", raw, 4)[0]
    assert abs(ver - 5.0) < 1e-9, f"包装版本异常: {ver}"
    return gzip.decompress(raw[12:])

def u32(p, o): return struct.unpack_from("<I", p, o)[0]
def d64(p, o): return struct.unpack_from("<d", p, o)[0]
CONST = 0x70241FF5

def find_node_section(p):
    cands = []
    for i in range(0, len(p) - 28, 4):
        if u32(p, i + 8) == 1 and u32(p, i + 12) == 136:
            n = u32(p, i + 16)
            if 1 <= n <= 10_000_000:
                cands.append((i, n))
    return cands

def parse_nodes(p, hdr, count, stride=52):
    nodes = {}
    base = hdr + 20
    for b in (base, base + 4):
        try:
            nid = u32(p, b)
            x = d64(p, b + 0xc); y = d64(p, b + 0x14); z = d64(p, b + 0x1c)
        except struct.error:
            continue
        if 1 <= nid <= 10_000_000 and abs(x) < 1e12 and abs(y) < 1e12 and abs(z) < 1e12:
            break
    for k in range(count):
        rec = b + k * stride
        nid = u32(p, rec)
        x = d64(p, rec + 0xc); y = d64(p, rec + 0x14); z = d64(p, rec + 0x1c)
        nodes[nid] = Node(nid, x, y, z)
    return nodes, b

def find_elem_section(p):
    cands = []
    for i in range(0, len(p) - 16, 4):
        if u32(p, i) == 997 and u32(p, i + 4) == 3 and u32(p, i + 8) == 175:
            n = u32(p, i + 12)
            if 1 <= n <= 100_000_000:
                cands.append((i, n))
    return cands

def parse_elements(p, hdr, count, row_map):
    elems = {}
    # 标准记录: [0][0x01680000][r1..r4][0][1][CONST][eid+1][(eid+1)<<16|2][0]
    for i in range(hdr, len(p) - 0x30, 4):
        if u32(p, i) == 0 and u32(p, i + 4) == 0x01680000:
            refs = [u32(p, i + 8 + j * 4) for j in range(4)]
            eid = u32(p, i + 0x24) - 1
            if eid < 1 or all(r == 0 for r in refs):
                continue
            nodes = [row_map.get(r, r) for r in refs if r != 0]
            if eid not in elems:
                elems[eid] = Elem(eid, nodes)
    # 尾部环绕记录（无 [0][0x01680000] 前缀，refs 在 +0，eid = N）
    if len(elems) < count:
        for i in range(hdr + 0x20, len(p) - 0x30, 4):
            if u32(p, i + 0x20) == CONST and u32(p, i + 0x28) == 0x10019:
                refs = [u32(p, i + j * 4) for j in range(4)]
                nodes = [row_map.get(r, r) for r in refs if r != 0]
                if nodes:
                    eid = count
                    if eid not in elems:
                        elems[eid] = Elem(eid, nodes)
    return elems

def decode(path):
    p = load_payload(path)
    model = HMModel(db_version=d64(p, 4))
    ns = find_node_section(p)
    es = find_elem_section(p)
    if not ns:
        return model
    nhdr, ncount = ns[0]
    model.node_count = ncount
    model.node_section = nhdr
    nodes, base = parse_nodes(p, nhdr, ncount)
    model.nodes = nodes
    row_order = []
    for k in range(ncount):
        rec = base + k * 52
        row_order.append(u32(p, rec))
    row_map = {k + 1: nid for k, nid in enumerate(row_order)}
    if es:
        ehdr, ecount = es[0]
        model.elem_count = ecount
        model.elem_section = ehdr
        model.elements = parse_elements(p, ehdr, ecount, row_map)
    return model

if __name__ == "__main__":
    import sys
    for path in sys.argv[1:]:
        m = decode(path)
        print(f"{path.split('/')[-1]}: db={m.db_version} nodes={len(m.nodes)}/{m.node_count} elems={len(m.elements)}/{m.elem_count}")
