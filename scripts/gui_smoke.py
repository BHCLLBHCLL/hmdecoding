#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hm_gui 无头逻辑冒烟测试: 不创建 QApplication, 直接验证模型/命令/VTK 构建."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import vtk  # noqa: F401
from hmdecoder import decode
import hm_gui as G

t0 = time.time()
m = decode("WS_3.2_3d_tetra_finish.hm")
print(f"decode: {len(m.nodes)} nodes, {len(m.elements)} elems, {time.time()-t0:.1f}s")

em = G.EditableModel(m, source_path="WS_3.2_3d_tetra_finish.hm")
print("groups:", dict(em.config_groups()))

# VTK 构建
import numpy as np
nids = sorted(em.nodes)
nid2idx = {n: i for i, n in enumerate(nids)}
xyz = np.array([[em.nodes[n].x, em.nodes[n].y, em.nodes[n].z] for n in nids])
vpts = vtk.vtkPoints()
vpts.SetData(G.numpy_to_vtk(xyz, deep=True))

by_cfg = {}
for i, e in enumerate(em.elements):
    by_cfg.setdefault(e.config, []).append((i, e))
for cfg, lst in sorted(by_cfg.items()):
    grid, skipped = G.build_group_grid(vpts, nid2idx, lst)
    arr = grid.GetCellData().GetArray("elem_idx")
    print(f"  cfg {cfg} {G.config_info(cfg)[0]}: cells={grid.GetNumberOfCells()} "
          f"skipped={skipped} elem_idx_arr={'OK' if arr else 'MISSING'}")
    assert grid.GetNumberOfCells() == len(lst), "单元数不符"
    assert arr is not None and arr.GetNumberOfTuples() == len(lst)

cloud = G.build_node_cloud(vpts, nids)
assert cloud.GetNumberOfCells() == len(nids)
print(f"node cloud: {cloud.GetNumberOfCells()} verts")

# 显示点/几何点构建 (空也应工作)
pd, ids = G.build_points_poly(em.display_points)
print(f"disp points poly: {pd.GetNumberOfPoints()} pts")

# ---- 编辑命令 + 撤销 ----
n0 = len(em.nodes)
e0 = len(em.elements)

# 1. 添加节点
em.apply(G.CmdAddNode(999999, (1.0, 2.0, 3.0)))
assert len(em.nodes) == n0 + 1 and em.nodes[999999].z == 3.0
em.undo()
assert len(em.nodes) == n0
em.redo()
assert len(em.nodes) == n0 + 1

# 2. 移动节点
em.apply(G.CmdMoveNodes([(999999, (1.0, 2.0, 3.0), (5.0, 6.0, 7.0))]))
assert em.nodes[999999].x == 5.0
em.undo()
assert em.nodes[999999].x == 1.0

# 3. 添加单元 (TRIA3 用三个真实节点 + 新节点)
some = nids[:2] + [999999]
em.apply(G.CmdAddElements([G.Elem(888888, some, 103)]))
assert len(em.elements) == e0 + 1
em.undo()
assert len(em.elements) == e0

# 4. 删除单元 (前 10 个)
em.apply(G.CmdDeleteElements(em, range(10)))
assert len(em.elements) == e0 - 10
em.undo()
assert len(em.elements) == e0

# 5. 删除节点连带
victim = em.elements[0].nodes[0]
attached = len(em.elements_of_nodes([victim]))
em.apply(G.CmdDeleteNodes(em, [victim]))
assert victim not in em.nodes
assert len(em.elements) == e0 - attached
em.undo()
assert victim in em.nodes and len(em.elements) == e0
print(f"delete node {victim}: attached elems = {attached}, undo OK")

# 6. 重编号
old_nid = nids[100]
em.apply(G.CmdRenumberNode(old_nid, 999998))
assert 999998 in em.nodes and old_nid not in em.nodes
assert any(999998 in e.nodes for e in em.elements)
em.undo()
assert old_nid in em.nodes and 999998 not in em.nodes

old_eid = em.elements[5].id
em.apply(G.CmdRenumberElements(old_eid, 987654))
assert em.elements[5].id == 987654
em.undo()
assert em.elements[5].id == old_eid

# 7. 翻转
tria_idx = next(i for i, e in enumerate(em.elements) if e.config == 103)
before = list(em.elements[tria_idx].nodes)
em.apply(G.CmdFlipElements([tria_idx]))
assert em.elements[tria_idx].nodes == before[::-1]
em.undo()
assert em.elements[tria_idx].nodes == before

# 8. JSON 往返
em.save_json("output/_smoke.hmj")
em2 = G.EditableModel.from_json("output/_smoke.hmj")
assert len(em2.nodes) == len(em.nodes) and len(em2.elements) == len(em.elements)
assert em2.nodes[999999].x == 1.0
print("json roundtrip OK")

# 9. to_hmmodel + INP 导出
hm = em.to_hmmodel()
from hmdecoder.export import export_inp
export_inp(hm, "output/_smoke.inp")
print("inp export OK")

# 10. ID 解析
assert G.SelectByIdDialog.parse_ids("1 2,3 10-12") == {1, 2, 3, 10, 11, 12}
print("id parse OK")

print(f"\nALL SMOKE TESTS PASSED ({time.time()-t0:.1f}s)")
