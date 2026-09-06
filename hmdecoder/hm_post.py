"""hm_post — 后处理骨架 (M8.2 起步).

按 DEV_PLAN.md §5 M8 目标:
  M8.1 结果解码 (.h3d/.res) -- NYI (需 hmbatch + 第三方格式逆向, NYI-M8-1)
  M8.2 Post 页 contour/deformed/... -- 本模块给伪 contour (不依赖结果文件)
  M8.3 XYPlots -- NYI (M8.3)
  M8.4 多视口 -- NYI (M8.4)
  M8.5 Morphing/Connectors -- NYI (M8.5)

pseudo_contour_field(model, mode='distance_to_centroid'):
  根据当前节点坐标 + 包围盒中心, 生成伪标量场 (每节点一个 float).
  模式:
    'distance_to_centroid' -- 节点到包围盒中心的欧氏距离
    'distance_to_origin'   -- 节点到原点的距离
    'z_height'             -- 节点 z 分量
    'id_modulo'            -- 节点 id % 100 (纯示意)
  返回 dict[nid] -> float

用法:
  from hmdecoder.hm_post import pseudo_contour_field, color_band
  field = pseudo_contour_field(model, 'distance_to_centroid')
  # VTK 标量映射
  scalars = color_band(field, n_bands=10)  # -> dict[nid] -> int (band index)
"""
from collections import defaultdict


def _bbox(nodes):
    if not nodes:
        return (0, 0, 0, 0, 0, 0)
    xs = [n.x for n in nodes]
    ys = [n.y for n in nodes]
    zs = [n.z for n in nodes]
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


def pseudo_contour_field(model, mode="distance_to_centroid"):
    """生成伪标量场, 用于在 VTK 中给节点标量映射 (无结果文件时演示)."""
    nodes = model.nodes
    if not nodes:
        return {}
    if mode == "distance_to_centroid":
        xmin, xmax, ymin, ymax, zmin, zmax = _bbox(nodes.values())
        cx = (xmin + xmax) / 2
        cy = (ymin + ymax) / 2
        cz = (zmin + zmax) / 2
        return {nid: ((n.x - cx) ** 2 + (n.y - cy) ** 2 + (n.z - cz) ** 2) ** 0.5
                for nid, n in nodes.items()}
    if mode == "distance_to_origin":
        return {nid: (n.x ** 2 + n.y ** 2 + n.z ** 2) ** 0.5
                for nid, n in nodes.items()}
    if mode == "z_height":
        return {nid: n.z for nid, n in nodes.items()}
    if mode == "id_modulo":
        return {nid: nid % 100 for nid, n in nodes.items()}
    raise ValueError(f"unknown pseudo contour mode: {mode}")


def color_band(field, n_bands=10):
    """把连续标量场量化为 n_bands 段: dict[nid] -> band_index."""
    if not field:
        return {}
    lo = min(field.values())
    hi = max(field.values())
    if hi <= lo:
        return {nid: 0 for nid in field}
    span = (hi - lo) / n_bands
    if span <= 0:
        return {nid: 0 for nid in field}
    return {nid: min(n_bands - 1, int((v - lo) / span))
            for nid, v in field.items()}


def field_stats(field):
    """场量统计: min/max/avg, 用于 contour 面板报告."""
    if not field:
        return "(empty field)"
    vs = list(field.values())
    lo, hi = min(vs), max(vs)
    avg = sum(vs) / len(vs)
    return f"min={lo:.6g} max={hi:.6g} avg={avg:.6g} n={len(vs)}"


# 列出场量模式供 GUI ComboBox
FIELD_MODES = [
    "distance_to_centroid",
    "distance_to_origin",
    "z_height",
    "id_modulo",
]