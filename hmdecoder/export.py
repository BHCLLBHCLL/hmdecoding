#!/usr/bin/env python3
"""hmdecoder.export — 将解码模型导出为 Abaqus INP（真实 ID/拓扑）。"""
from .decoder import HMModel

# HyperMesh config -> Abaqus 单元类型（按节点数保守映射，注释保留 config 号）
def inp_type(config: int, n_nodes: int) -> str:
    if n_nodes == 3:
        return "S3"          # tria3
    if n_nodes == 4:
        return "S4"          # quad4
    if n_nodes == 6:
        return "C3D6"
    if n_nodes == 8:
        return "C3D8"
    if n_nodes == 10:
        return "C3D10"
    return f"ELEM{n_nodes}"

def export_inp(model: HMModel, path: str, title: str = "HyperMesh model decoded by hmdecoder"):
    from collections import defaultdict
    groups = defaultdict(list)
    for e in model.elements.values():
        groups[(e.config, len(e.nodes))].append(e)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"*HEADING\n{title}\n")
        f.write(f"** Decoded by hmdecoder: {len(model.nodes)} nodes, {len(model.elements)} elements\n")
        f.write(f"** DB version: {model.db_version}\n\n")
        f.write("*NODE\n")
        for nid in sorted(model.nodes):
            n = model.nodes[nid]
            f.write(f"{nid}, {n.x:.8e}, {n.y:.8e}, {n.z:.8e}\n")
        f.write("\n")
        for (config, nn), elems in sorted(groups.items()):
            t = inp_type(config, nn)
            f.write(f"*ELEMENT, TYPE={t}\n")
            f.write(f"** config={config}, nodes={nn}\n")
            for e in sorted(elems, key=lambda e: e.id):
                f.write(f"{e.id}, " + ", ".join(str(n) for n in e.nodes) + "\n")
            f.write(f"*ELSET, ELSET=SET_CONFIG{config}\n")
            ids = [str(e.id) for e in sorted(elems, key=lambda e: e.id)]
            for i in range(0, len(ids), 16):
                f.write(", ".join(ids[i:i+16]) + "\n")
            f.write("\n")
