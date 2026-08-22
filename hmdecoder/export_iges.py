#!/usr/bin/env python3
"""hmdecoder.export_iges — 将解码几何（点/线）导出为 IGES 5.3 固定格式。"""
from .decoder import HMModel


def export_iges(model: HMModel, path: str):
    """导出几何点（+变体 A 推断线）为 IGES 5.3 固定格式。"""
    points = [(pid, gp.x, gp.y, gp.z) for pid, gp in sorted(model.geo_points.items())]
    lines = list(getattr(model, "_variant_a_lines", []) or [])
    pidx = {p[0]: (p[1], p[2], p[3]) for p in points}

    rows = []
    def add(section, seq, text):
        for i in range(0, len(text), 72):
            rows.append(text[i:i+72].ljust(72) + section + str(seq).rjust(7))
            seq += 1
        return seq

    seq = add("S", 1, "IGES geometry exported by hmdecoder")
    g = "1H,,1H;,4H    ,,8HHMDECODE,32,38,64,6,99,2,2Hmm,1.0,1.0,15H20260101.000000,1.0E-06,1.0E+07,8Hhmdecode,8Hhmdecode,8H2019.0.0,1.0E-06,8Hhmdecode,1,1,15H20260101.000000,15H20260101.000000;"
    seq = add("G", seq, g)

    # 实体: (type, params_text, param_lines)
    ents = []
    for pid, x, y, z in points:
        ents.append((116, f"{x},{y},{z};", 1))
    for lid, p1, p2 in lines:
        if p1 in pidx and p2 in pidx:
            x1, y1, z1 = pidx[p1]
            x2, y2, z2 = pidx[p2]
            ents.append((110, f"{x1},{y1},{z1},{x2},{y2},{z2};", 1))
    # 移除非 116 实体（线引用缺失点）
    ents = [e for e in ents if e[0] == 116] + [e for e in ents if e[0] == 110]

    dstart = seq
    pd = 1
    for typ, params, plines in ents:
        label = str(typ)
        r1 = f"{typ:>8}{pd:>8}{0:>8}{0:>8}{1:>8}{0:>8}{0:>8}{0:>8}{0:>8}"
        r2 = f"{typ:>8}{1:>8}{1:>8}{plines:>8}{0:>8}{0:>8}{0:>8}{label:>8}{0:>8}"
        seq = add("D", seq, r1)
        seq = add("D", seq, r2)
        pd += plines
    dend = seq - 1
    pstart = seq
    for typ, params, plines in ents:
        seq = add("P", seq, params)
    pend = seq - 1
    t = f"S{1:>7}G{2:>7}D{dend:>7}P{pend:>7}      T{1:>7}"
    rows.append(t.ljust(72) + "T" + str(seq).rjust(7))
    with open(path, "w", encoding="ascii") as f:
        f.write("\n".join(rows))
    return len(points), len([e for e in ents if e[0] == 110])
