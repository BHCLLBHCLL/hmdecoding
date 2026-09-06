"""hm_card — 求解器 Card image 骨架 (M6.1).

按 DEV_PLAN.md §5 M6.1 目标, 提供 4 张基础卡片的字段模板:
  PSHELL / PSOLID / MAT1 / CQUAD4

不进行 HM 内部 card image 二进制逆向 (需 hwtemplex.dll + hmbatch oracle), 仅
给出标准 Nastran 卡片格式 + HM 2019 面板习惯字段顺序, 让 Analysis/card edit
面板从 NYI 灰显升级为可用 (以 collector comp/mat/prop 名为载体展示).

登记在 NYI-M6-1: Card image 解码仍需 hmbatch oracle 闭环, 当前 skeleton 仅
保证卡片字段顺序与 HM UI 面板 (card edit) 视觉一致.
"""

CARD_TEMPLATES = {
    "PSHELL": {
        "long": "PSHELL - Shell Property",
        "fields": [
            ("PID",    "int",   "Property ID"),
            ("MID",    "int",   "Material ID"),
            ("T",      "float", "Thickness"),
            ("MID2",   "int",   "Material ID for bending"),
            ("12I/T3", "float", "12*I/T^3 (bending)"),
            ("MID3",   "int",   "Material ID for transverse shear"),
            ("TS/T",   "float", "Transverse shear thickness"),
            ("NSM",    "float", "Non-structural mass per unit area"),
            ("Z1",     "float", "Fibre distance Z1 (composite)"),
            ("Z2",     "float", "Fibre distance Z2 (composite)"),
            ("MID4",   "int",   "Material ID for membrane-bending coupling"),
        ],
    },
    "PSOLID": {
        "long": "PSOLID - Solid Property",
        "fields": [
            ("PID",    "int",   "Property ID"),
            ("MID",    "int",   "Material ID"),
            ("CORDM",  "int",   "Material coordinate system"),
            ("IN",     "int",   "Integration scheme"),
            ("STRESS", "str",   "Stress output: 'GRID' or 'GAUSS'"),
            ("ISOP",   "int",   "Isotropic material flag"),
            ("FCTN",   "str",   "Failure function theory"),
        ],
    },
    "MAT1": {
        "long": "MAT1 - Isotropic Material",
        "fields": [
            ("MID",  "int",   "Material ID"),
            ("E",    "float", "Young's modulus"),
            ("G",    "float", "Shear modulus"),
            ("NU",   "float", "Poisson's ratio"),
            ("RHO",  "float", "Mass density"),
            ("A",    "float", "Thermal expansion coefficient"),
            ("TREF", "float", "Reference temperature"),
            ("GE",   "float", "Damping coefficient"),
            ("ST",   "float", "Stress limit"),
            ("SC",   "float", "Stress limit compression"),
            ("SS",   "float", "Stress limit shear"),
        ],
    },
    "CQUAD4": {
        "long": "CQUAD4 - Quadrilateral Element",
        "fields": [
            ("EID",  "int", "Element ID"),
            ("PID",  "int", "Property ID"),
            ("G1",   "int", "Grid point 1"),
            ("G2",   "int", "Grid point 2"),
            ("G3",   "int", "Grid point 3"),
            ("G4",   "int", "Grid point 4"),
            ("THETA","float", "Material angle"),
            ("ZOFFS","float", "Offset"),
            ("TFLAG","int",   "Thickness flag"),
            ("T1",   "float", "Thickness at G1"),
            ("T2",   "float", "Thickness at G2"),
            ("T3",   "float", "Thickness at G3"),
            ("T4",   "float", "Thickness at G4"),
        ],
    },
}


def list_templates():
    """返回所有已知卡片名列表 (供 GUI ComboBox)."""
    return sorted(CARD_TEMPLATES.keys())


def get_template(name):
    """取卡片模板, 不区分大小写; 找不到返回 None."""
    return CARD_TEMPLATES.get(name.upper())


def format_card_text(name, values=None):
    """格式化卡片为 8-char 字段对齐的文本 (Nastran BDF 风格).

    values: dict[field_name] -> str|int|float (按字段顺序)
    返回: 多行 string (每行 80 字符, 字段按 8-char 对齐)
    """
    tpl = get_template(name)
    if not tpl:
        return f"[unknown card: {name}]"
    values = values or {}
    rows = [f"{name:<8}"]
    line_buf = name.ljust(8)
    line_pos = 1
    for fname, ftype, _desc in tpl["fields"]:
        v = values.get(fname, "")
        if isinstance(v, float):
            v = f"{v:.6g}"
        chunk = str(v)[:8].ljust(8)
        if line_pos >= 9:
            rows.append(line_buf.rstrip())
            line_buf = " " * 8
            line_pos = 0
        line_buf += chunk
        line_pos += 1
    if line_buf.strip():
        rows.append(line_buf.rstrip())
    return "\n".join(rows)


def card_summary_html(name, values=None):
    """卡片摘要 HTML (供 GUI Entity Editor 渲染)."""
    tpl = get_template(name)
    if not tpl:
        return f"<i>unknown card: {name}</i>"
    values = values or {}
    lines = [f"<b>{tpl['long']}</b>", "<table border=1 cellpadding=3 "
                                       "style='border-collapse:collapse;font-family:monospace'>",
             "<tr><th>Field</th><th>Type</th><th>Value</th><th>Description</th></tr>"]
    for fname, ftype, desc in tpl["fields"]:
        v = values.get(fname, "")
        if isinstance(v, float):
            v = f"{v:.6g}"
        lines.append(f"<tr><td>{fname}</td><td>{ftype}</td>"
                     f"<td><b>{v}</b></td><td>{desc}</td></tr>")
    lines.append("</table>")
    return "\n".join(lines)