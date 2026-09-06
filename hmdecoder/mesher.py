"""hm_mesher — 网格生成/平滑骨架 (M7.2 起步).

按 DEV_PLAN.md §5 M7 目标:
  M7.1 2D automesh   -- NYI (需几何 record 解码, 见 NYI-M4-2/3/4)
  M7.2 smooth        -- Laplacian 平滑骨架 (本模块实现)
  M7.3 3D tetramesh  -- NYI (需 Delaunay 实现, 工业级内核, NYI)
  M7.4 hex map       -- NYI
  M7.5 对拍          -- 待 M7.2/3 后接入

laplacian_smooth_2d(model, iterations=5):
  对每个内部节点, 坐标 = 邻接节点几何平均; 边界节点不动.
  邻接关系通过单元拓扑 (quad/tri) 建立, 不依赖几何 record.

用法:
  from hmdecoder.mesher import laplacian_smooth_2d
  new_nodes = laplacian_smooth_2d(model, iterations=5)
  # new_nodes 是新 dict[id] -> (x,y,z); 调用方决定是否替换 model.nodes
"""
from collections import defaultdict


def _build_node_adjacency(nodes, elements):
    """从单元拓扑建立节点邻接: {nid: set(邻居 nid)}.

    适用于任意单元类型 (quad/tri/tetra/hex). 每个单元的所有节点彼此邻接.
    """
    adj = defaultdict(set)
    nodes_set = set(nodes)
    for e in elements:
        ns = [n for n in e.nodes if n in nodes_set]
        for i in range(len(ns)):
            for j in range(i + 1, len(ns)):
                adj[ns[i]].add(ns[j])
                adj[ns[j]].add(ns[i])
    return adj


def _detect_boundary(adj):
    """边界节点 = 邻接数 < 6 (2D quad 内部节点=8 邻居, 边界=5, 角=3).

    简化判据: 邻接数 ≤ 5 视为边界. 覆盖 quad 网格所有边界/角点情形.
    对 tri/3D 网格可参数化 (本骨架固定为 quad 习惯, 三角网格需后续调整).
    """
    boundary = set()
    for nid, neigh in adj.items():
        if len(neigh) <= 5:
            boundary.add(nid)
    return boundary


def laplacian_smooth_2d(model, iterations=5, fix_boundary=True):
    """Laplacian 平滑 (M7.2 骨架).

    对每个内部节点, 新坐标 = 邻接节点坐标平均; 边界节点保持不动.
    迭代 iterations 次. 返回新节点 dict (不修改原 model).

    Args:
        model: HMModel (nodes dict + elements list)
        iterations: 平滑迭代次数
        fix_boundary: True = 边界节点坐标不动 (default); False = 全员平滑

    Returns:
        dict[id] -> (x, y, z)
    """
    if not model.nodes or not model.elements:
        return dict(model.nodes)
    adj = _build_node_adjacency(model.nodes, model.elements)
    boundary = _detect_boundary(adj) if fix_boundary else set()

    new_nodes = {}
    cur = {nid: (n.x, n.y, n.z) for nid, n in model.nodes.items()}
    for it in range(iterations):
        nxt = {}
        for nid, (x, y, z) in cur.items():
            if nid in boundary:
                nxt[nid] = (x, y, z)
                continue
            neigh = adj.get(nid, set())
            if not neigh:
                nxt[nid] = (x, y, z)
                continue
            sx = sy = sz = 0.0
            cnt = 0
            for nb in neigh:
                if nb in cur:
                    nx, ny, nz = cur[nb]
                    sx += nx; sy += ny; sz += nz
                    cnt += 1
            if cnt == 0:
                nxt[nid] = (x, y, z)
            else:
                nxt[nid] = (sx / cnt, sy / cnt, sz / cnt)
        cur = nxt
    return cur


def smooth_quality_report(model, before_nodes=None, after_nodes=None):
    """网格质量报告: 平均边长变化 (内部节点).

    用于评估 Laplacian smooth 的影响; 量化对拍留 M7.5.
    """
    if before_nodes is None or after_nodes is None:
        return "(missing snapshots)"
    adj = _build_node_adjacency(model.nodes, model.elements)
    boundary = _detect_boundary(adj)
    diffs = []
    for nid in before_nodes:
        if nid in boundary:
            continue
        b = before_nodes[nid]
        a = after_nodes.get(nid, b)
        d = ((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2) ** 0.5
        diffs.append(d)
    if not diffs:
        return "(no interior nodes)"
    avg = sum(diffs) / len(diffs)
    mx = max(diffs)
    return f"interior nodes={len(diffs)} avg_disp={avg:.6g} max_disp={mx:.6g}"