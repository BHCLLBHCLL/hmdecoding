#!/usr/bin/env python3
"""hmdecoder.export — 将解码模型导出为 STEP AP203（基于单元面的网格几何）。"""
from .decoder import HMModel


def export_step(model: HMModel, path: str, title: str = "HyperMesh model decoded by hmdecoder"):
    """将单元面导出为 SHELL_BASED_SURFACE_MODEL（OPEN_SHELL + FACE_SURFACE/PLANE）。
    每个单元生成独立面（不共享边），顶点按节点共享。"""
    fid = 1
    def nxt():
        nonlocal fid
        v = fid
        fid += 1
        return v

    lines = []
    lines.append("ISO-10303-21;")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('HyperMesh mesh geometry decoded by hmdecoder'),'2;1');")
    lines.append(f"FILE_NAME('{path.split('/')[-1]}','',('hmdecoder'),(''),'hmdecoder','HyperMesh','');")
    lines.append("FILE_SCHEMA(('CONFIG_CONTROL_DESIGN'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")

    # 应用上下文
    ctx = nxt(); lines.append(f"#{ctx} = APPLICATION_CONTEXT('configuration control 3D design');")
    apd = nxt(); lines.append(f"#{apd} = APPLICATION_PROTOCOL_DEFINITION('international standard','config_control_design',1994,#{ctx});")
    # 单位（mm）
    u1 = nxt(); lines.append(f"#{u1} = ( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) );")
    u2 = nxt(); lines.append(f"#{u2} = ( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) );")
    u3 = nxt(); lines.append(f"#{u3} = ( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() );")
    unc = nxt(); lines.append(f"#{unc} = UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-06),#{u1},'distance_accuracy_value','Maximum model space deviation');")
    gctx = nxt(); lines.append(f"#{gctx} = ( GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc})) GLOBAL_UNIT_ASSIGNED_CONTEXT((#{u1},#{u2},#{u3})) REPRESENTATION_CONTEXT('','') );")

    # 节点 -> CARTESIAN_POINT + VERTEX_POINT
    vertex_of = {}
    for nid, n in model.nodes.items():
        cp = nxt(); lines.append(f"#{cp} = CARTESIAN_POINT('',({n.x:.8e},{n.y:.8e},{n.z:.8e}));")
        vp = nxt(); lines.append(f"#{vp} = VERTEX_POINT('',#{cp});")
        vertex_of[nid] = vp

    shells = []
    for e in model.elements.values():
        if len(e.nodes) < 3:
            continue
        # PLANE: 用前 3 个节点
        p0 = model.nodes[e.nodes[0]]
        p1 = model.nodes[e.nodes[1]]
        p2 = model.nodes[e.nodes[2]]
        pl = nxt()
        lines.append(f"#{pl} = PLANE('',#{gctx},(0.0,0.0,1.0));")  # 简化: 法向占位
        # 边
        n = len(e.nodes)
        oriented = []
        for i in range(n):
            a = e.nodes[i]
            b = e.nodes[(i + 1) % n]
            va = vertex_of[a]; vb = vertex_of[b]
            ln = nxt(); lines.append(f"#{ln} = LINE('',#{vertex_of[a]},(1.0,0.0,0.0));")
            ec = nxt(); lines.append(f"#{ec} = EDGE_CURVE('',#{va},#{vb},#{ln},.T.);")
            oe = nxt(); lines.append(f"#{oe} = ORIENTED_EDGE('',*,*,#{ec},.T.);")
            oriented.append(f"#{oe}")
        loop = nxt(); lines.append(f"#{loop} = EDGE_LOOP('',({','.join(oriented)}));")
        bound = nxt(); lines.append(f"#{bound} = FACE_OUTER_BOUND('',#{loop},.T.);")
        face = nxt(); lines.append(f"#{face} = FACE_SURFACE('',(#{bound}),#{pl},.T.);")
        shells.append(f"#{face}")

    oshell = nxt(); lines.append(f"#{oshell} = OPEN_SHELL('',({','.join(shells)}));")
    rep = nxt(); lines.append(f"#{rep} = SHAPE_REPRESENTATION('mesh',(#{oshell}),#{gctx});")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return fid
