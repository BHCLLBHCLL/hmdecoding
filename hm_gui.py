#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hm_gui.py — HyperMesh .hm 模型 解析 / 3D 显示 / 编辑 一体化 GUI

工作区对齐 Altair HyperMesh 2019 经典界面 (hmopengl.exe +
help/hm/topics/chapter_heads/workspace_hm_classic_r.htm):
  Title / Menu / Toolbars / Tab Area (Utility·Mask·Model) /
  Modeling Window / Panel Area (Geom 1D 2D 3D Analysis Tool Post) /
  Entity Editor / Status Bar

界面风格参考 D:/training/cgns/pphdecoding (浅色 Fusion + 蓝标题条).

功能
----
- 解析: 基于本仓库 hmdecoder 差分逆向解码器
- 显示: PyQt5 + VTK 9; 按单元 config 分组着色; 四种显示模式
- 选择: 单击拾取, Ctrl 多选, 橡皮筋框选, 按 ID 选择
- 编辑: 移动/添加/删除节点与单元, 翻转法向, 重编号, 命令式撤销/重做
- 导出: Abaqus INP / STEP / IGES / CSV; .hmj 工程

运行: python hm_gui.py [模型.hm|.hm10|.hmj]
"""
import json
import os
import re
import sys
import time
import traceback
from collections import Counter
from pathlib import Path

import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import (
    QBrush, QColor, QFont, QIcon, QPainter, QPen, QPixmap, QPolygon,
)
from PyQt5.QtWidgets import (
    QAction, QApplication, QButtonGroup, QCheckBox, QComboBox, QDialog,
    QDialogButtonBox, QDoubleSpinBox, QFileDialog, QFormLayout, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView, QInputDialog, QLabel,
    QLineEdit, QMainWindow, QMenu, QMessageBox, QPlainTextEdit, QProgressDialog,
    QPushButton, QRadioButton, QSizePolicy, QSpinBox, QSplitter,
    QStackedWidget, QStyle, QTabWidget, QTableWidget, QTableWidgetItem,
    QTextBrowser, QToolBar, QToolButton, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget,
)

import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.util.numpy_support import numpy_to_vtk

import vtkmodules.vtkInteractionStyle  # noqa: F401  (确保交互样式注册)
import vtkmodules.vtkRenderingOpenGL2  # noqa: F401  (确保 OpenGL2 后端注册)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hmdecoder import decode, Elem, HMModel, Node  # noqa: E402
from hmdecoder.decoder import DisplayPoint, GeoPoint  # noqa: E402

APP_TITLE = "HyperMesh 2019"
HM_PROFILE_DEFAULT = "Abaqus (Explicit)"
ALTAIR_ROOT = Path(r"C:/Program Files/Altair/2019")
HM_HELP_UI = ALTAIR_ROOT / "help" / "hm" / "topics" / "chapter_heads" / "workspace_hm_classic_r.htm"
HM_HELP_PANELS = ALTAIR_ROOT / "help" / "hm" / "topics" / "panels" / "panels_r.htm"

# 视口渐变: 对齐 HM 2019 打开案例时的深蓝建模窗口 (顶 #334C66 → 底 #1A2633)
HM_BG_DARK_TOP = (0.200, 0.298, 0.400)
HM_BG_DARK_BOT = (0.102, 0.149, 0.200)
HM_BG_LIGHT_TOP = (0.46, 0.56, 0.70)
HM_BG_LIGHT_BOT = (0.84, 0.87, 0.91)
HM_BG_TOP = HM_BG_DARK_TOP
HM_BG_BOT = HM_BG_DARK_BOT

HM_PAGE_LABELS = {
    "Geom": "Geometry", "1D": "1D", "2D": "2D", "3D": "3D",
    "Analysis": "Analysis", "Tool": "Tool", "Post": "Post",
}

# 材料库预置 (求解器卡片语义未解码时的参考目录)
HM_MAT_LIBRARY = (
    ("Steel", "MAT1", 7.85e-9, 210000.0, 0.30),
    ("Aluminum", "MAT1", 2.70e-9, 70000.0, 0.33),
    ("Titanium", "MAT1", 4.43e-9, 110000.0, 0.32),
    ("Cast Iron", "MAT1", 7.20e-9, 120000.0, 0.26),
    ("ABS", "MAT1", 1.05e-9, 2300.0, 0.35),
    ("Rubber", "HYPER", 1.10e-9, 10.0, 0.49),
    ("Glass", "MAT1", 2.50e-9, 70000.0, 0.23),
    ("Copper", "MAT1", 8.96e-9, 110000.0, 0.34),
)

# 底部面板页: 官方 page menu (help/hm/topics/panels/panels_r.htm + 2019 截图)
# 每页是列列表, 每列自上而下的面板名. 已实现的面板会打开对应功能, 其余提示 NYI.
HM_PANEL_PAGES = {
    "Geom": [
        ["nodes", "node edit", "temp nodes", "distance", "points"],
        ["lines", "line edit", "length"],
        ["surfaces", "surface edit", "defeature", "midsurface", "dimensioning"],
        ["solids", "solid edit", "ribs"],
        ["quick edit", "edge edit", "point edit", "autocleanup"],
    ],
    "1D": [
        ["masses", "rods", "bars", "beams"],
        ["springs", "dampers", "gaps", "plotel"],
        ["rigids", "rigidlinks", "rbe3", "equations"],
        ["welds", "spotweld", "connectors"],
        ["line mesh", "1D mesh", "elem types"],
    ],
    "2D": [
        ["automesh", "smooth", "qualityindex", "cleanup"],
        ["elem offset", "shrink", "split", "combine"],
        ["edit element", "replace", "order change"],
        ["ruled", "spin", "drag", "spline", "skin"],
        ["elem types", "elem cleanup", "features"],
    ],
    "3D": [
        ["tetramesh", "hex mesh", "solid map"],
        ["drag", "spin", "elem offset"],
        ["split", "combine", "replace"],
        ["edit element", "elem types"],
        ["qualityindex", "smooth"],
    ],
    "Analysis": [
        ["loadcols", "constraints", "forces"],
        ["moments", "pressures", "temperatures"],
        ["velocities", "accelerations", "equations"],
        ["systems", "vectors", "output blocks"],
        ["loadsteps", "control cards", "card edit"],
    ],
    "Tool": [
        ["translate", "rotate", "reflect", "scale"],
        ["project", "position", "permute"],
        ["numbers", "find", "mask", "isolate"],
        ["organize", "renumber", "count"],
        ["distance", "edges", "faces", "features"],
    ],
    "Post": [
        ["contour", "vectors", "deformation"],
        ["isosurfaces", "section cut", "query"],
        ["title", "legend", "animate"],
        ["transient", "derived loadsteps"],
    ],
}

HM_QSS = """
QMainWindow { background: #f0f0f0; }
QMenuBar { background: #f0f0f0; border-bottom: 1px solid #b8b8b8; padding: 1px; }
QMenuBar::item { padding: 3px 9px; }
QMenuBar::item:selected { background: #cde4f7; }
QMenu { background: #f7f7f7; border: 1px solid #a0a0a0; }
QMenu::item { padding: 3px 22px 3px 10px; }
QMenu::item:selected { background: #cde4f7; color: #000; }
QToolBar { background: #ececec; border: none; border-bottom: 1px solid #c0c0c0;
           spacing: 1px; padding: 1px 3px; }
QToolBar QToolButton {
    padding: 2px 3px; margin: 1px;
    border: 1px solid transparent; border-radius: 2px;
}
QToolBar QToolButton:hover { background: #d6ebf8; border: 1px solid #7eb6d9; }
QToolBar QToolButton:pressed { background: #b8d8ef; }
QToolBar QToolButton:checked { background: #b8d8ef; border: 1px solid #5a9ac6; }
QStatusBar { background: #ececec; border-top: 1px solid #b8b8b8; }
QStatusBar QLabel { padding: 0 6px; }
QSplitter::handle { background: #c4c4c4; width: 3px; height: 3px; }
QTabWidget::pane { border: 1px solid #9a9a9a; background: #ffffff; }
QTabBar::tab {
    background: #d8d8d8; border: 1px solid #9a9a9a; border-bottom: none;
    padding: 3px 11px; margin-right: 1px;
}
QTabBar::tab:selected { background: #ffffff; font-weight: bold; }
QTreeWidget, QPlainTextEdit, QTextBrowser, QTableWidget {
    background: #ffffff; border: none; font-size: 11px;
}
QTreeWidget#HmModelTree::item { height: 18px; padding: 1px 2px; }
QTreeWidget#HmModelTree::item:selected { background: #cde4f7; color: #111; }
QTreeWidget#HmModelTree::item:hover { background: #e8f3fb; }
QHeaderView::section {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #f6f6f6, stop:1 #e0e0e0);
    border: 1px solid #c0c0c0; padding: 2px 5px; font-weight: bold;
}
#PaneTitleBar {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #5b9bd5, stop:1 #2e75b6);
    color: white; font-weight: bold; font-size: 11px; padding: 3px 6px;
}
#PaneFrame { background: #ffffff; border: 1px solid #9a9a9a; }
#ViewStrip {
    background: #d8d8d8; border-right: 1px solid #9a9a9a;
}
#GfxBar {
    background: #e4e4e4; border-top: 1px solid #b0b0b0;
    border-bottom: 1px solid #9a9a9a;
}
#HmPanelBar { background: #dcdcdc; border-top: 1px solid #9a9a9a; }
QPushButton#HmPanelBtn {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #f3f3f3, stop:1 #c6c6c6);
    border: 1px solid #7a7a7a; border-top-color: #efefef;
    border-left-color: #efefef;
    padding: 2px 7px; min-width: 78px; min-height: 17px; font-size: 11px;
}
QPushButton#HmPanelBtn:hover { background: #e8e8e8; }
QPushButton#HmPanelBtn:pressed, QPushButton#HmPanelBtn:checked {
    background: #b8d0e8; border: 1px solid #3d7eaf;
}
QRadioButton#HmPageRadio { font-size: 11px; padding: 1px 2px; }
QComboBox { padding: 1px 4px; min-height: 18px; }
QLabel#ModelOverlay {
    color: #1a1a1a; background: transparent; font-size: 11px;
    font-family: "Segoe UI", Arial;
}
"""

# ---------------------------------------------------------------------------
# 单元 config 字典 (权威来源: templates/feoutput/hm/general — HM 原生模板)
#   config -> (名称, 标准节点数, 维度类别)   节点数 0 表示变长
# ---------------------------------------------------------------------------
CONFIG_TABLE = {
    1:   ("MASS",       1,  "0D"),
    2:   ("PLOTEL",     2,  "1D"),
    3:   ("WELD",       2,  "1D"),
    5:   ("RIGID",      2,  "1D"),
    21:  ("SPRING",     2,  "1D"),
    22:  ("JOINT",      2,  "1D"),
    23:  ("SPRING3N",   3,  "1D"),
    24:  ("SPRING4N",   4,  "1D"),
    27:  ("XELEM",      0,  "1D"),
    55:  ("RIGIDLINK",  0,  "1D"),   # 变长 (主-从)
    56:  ("RBE3",       0,  "1D"),   # 变长
    57:  ("ICE",        0,  "1D"),
    60:  ("BAR2",       2,  "1D"),
    61:  ("ROD",        2,  "1D"),
    63:  ("BAR3",       3,  "1D"),
    70:  ("GAP",        2,  "1D"),
    103: ("TRIA3",      3,  "2D"),
    104: ("QUAD4",      4,  "2D"),
    106: ("TRIA6",      6,  "2D"),
    108: ("QUAD8",      8,  "2D"),
    123: ("MASTER3",    3,  "2D"),
    124: ("MASTER4",    4,  "2D"),
    133: ("SLAVE3",     3,  "2D"),
    134: ("SLAVE4",     4,  "2D"),
    204: ("TETRA4",     4,  "3D"),
    205: ("PYRAMID5",   5,  "3D"),
    206: ("PENTA6",     6,  "3D"),
    208: ("HEXA8",      8,  "3D"),
    210: ("TETRA10",   10,  "3D"),
    213: ("PYRAMID13", 13,  "3D"),
    215: ("PENTA15",   15,  "3D"),
    220: ("HEXA20",    20,  "3D"),
}


def config_info(config):
    """config -> (名称, 标准节点数, 类别); 未知 config 返回占位."""
    return CONFIG_TABLE.get(config, (f"CFG{config}", 0, "?"))


def vtk_cell_type(config, n):
    """按 (config, 实际节点数) 决定 VTK 单元类型; 返回 None 表示需扇形展开为线."""
    if n <= 0:
        return vtk.VTK_VERTEX
    # 二阶单元优先 (严格按 config)
    second = {63: vtk.VTK_QUADRATIC_EDGE, 106: vtk.VTK_QUADRATIC_TRIANGLE,
              108: vtk.VTK_QUADRATIC_QUAD, 210: vtk.VTK_QUADRATIC_TETRA,
              213: vtk.VTK_QUADRATIC_PYRAMID, 215: vtk.VTK_QUADRATIC_WEDGE,
              220: vtk.VTK_QUADRATIC_HEXAHEDRON}
    if config in second:
        return second[config]
    cat = config_info(config)[2]
    if cat == "3D":
        return {4: vtk.VTK_TETRA, 5: vtk.VTK_PYRAMID, 6: vtk.VTK_WEDGE,
                8: vtk.VTK_HEXAHEDRON}.get(n, vtk.VTK_CONVEX_POINT_SET)
    if cat == "2D":
        return {3: vtk.VTK_TRIANGLE, 4: vtk.VTK_QUAD}.get(n, vtk.VTK_POLYGON)
    # 0D/1D 与未知
    if n == 1:
        return vtk.VTK_VERTEX
    if n == 2:
        return vtk.VTK_LINE
    if cat == "?":
        return {3: vtk.VTK_TRIANGLE, 4: vtk.VTK_QUAD, 5: vtk.VTK_PYRAMID,
                6: vtk.VTK_WEDGE, 8: vtk.VTK_HEXAHEDRON}.get(n, vtk.VTK_POLY_LINE)
    return None  # RIGIDLINK/RBE3 等变长: 扇形展开 (首节点 -> 其余)


# 分组调色板 (首色对齐 HM 2019 案例的洋红网格)
PALETTE = [
    (0.82, 0.28, 0.70), (0.36, 0.62, 0.85), (0.45, 0.78, 0.45),
    (0.93, 0.68, 0.30), (0.75, 0.55, 0.85), (0.40, 0.80, 0.75),
    (0.90, 0.45, 0.35), (0.60, 0.75, 0.35), (0.55, 0.55, 0.80),
    (0.85, 0.80, 0.40), (0.50, 0.70, 0.55), (0.80, 0.60, 0.50),
    (0.45, 0.55, 0.75), (0.70, 0.50, 0.65), (0.55, 0.85, 0.60),
    (0.90, 0.75, 0.55), (0.50, 0.60, 0.90), (0.75, 0.85, 0.45),
    (0.85, 0.50, 0.55), (0.45, 0.75, 0.85), (0.70, 0.65, 0.35),
    (0.60, 0.45, 0.70), (0.55, 0.70, 0.40), (0.88, 0.60, 0.75),
]

DISPLAY_MODES = ("实体表面", "表面+边", "线框", "点")


# ---------------------------------------------------------------------------
# 可编辑模型 + 命令式撤销
# ---------------------------------------------------------------------------
class Command:
    """编辑命令基类: redo/undo 成对实现, 栈式撤销 (逆序撤销保证索引一致)."""
    label = "编辑"

    def redo(self, model):  # pragma: no cover - 抽象
        raise NotImplementedError

    def undo(self, model):  # pragma: no cover - 抽象
        raise NotImplementedError


class CmdMoveNodes(Command):
    label = "移动节点"

    def __init__(self, moves):  # moves: [(nid, (ox,oy,oz), (nx,ny,nz))]
        self.moves = moves

    def redo(self, model):
        for nid, _old, new in self.moves:
            n = model.nodes.get(nid)
            if n is not None:
                n.x, n.y, n.z = new

    def undo(self, model):
        for nid, old, _new in self.moves:
            n = model.nodes.get(nid)
            if n is not None:
                n.x, n.y, n.z = old


class CmdAddNode(Command):
    label = "添加节点"

    def __init__(self, nid, xyz):
        self.nid, self.xyz = nid, xyz

    def redo(self, model):
        model.nodes[self.nid] = Node(self.nid, *self.xyz)

    def undo(self, model):
        model.nodes.pop(self.nid, None)


class CmdAddElements(Command):
    label = "添加单元"

    def __init__(self, elems):  # elems: [Elem]
        self.elems = elems
        self.start = 0

    def redo(self, model):
        self.start = len(model.elements)
        model.elements.extend(self.elems)

    def undo(self, model):
        del model.elements[self.start:self.start + len(self.elems)]


class CmdDeleteElements(Command):
    label = "删除单元"

    def __init__(self, model, indices):
        # 存 (索引, 单元副本); 副本防别名
        self.items = [(i, Elem(e.id, list(e.nodes), e.config))
                      for i, e in ((i, model.elements[i]) for i in sorted(indices))]

    def redo(self, model):
        for i, _e in reversed(self.items):
            del model.elements[i]

    def undo(self, model):
        for i, e in self.items:
            model.elements.insert(i, Elem(e.id, list(e.nodes), e.config))


class CmdDeleteNodes(Command):
    label = "删除节点"

    def __init__(self, model, nids):
        self.nids = [n for n in nids if n in model.nodes]
        self.nodes = [(n, model.nodes[n].x, model.nodes[n].y, model.nodes[n].z)
                      for n in self.nids]
        ns = set(self.nids)
        self.elems = [(i, Elem(e.id, list(e.nodes), e.config))
                      for i, e in enumerate(model.elements)
                      if any(nd in ns for nd in e.nodes)]

    def redo(self, model):
        for i, _e in reversed(self.elems):
            del model.elements[i]
        for n in self.nids:
            model.nodes.pop(n, None)

    def undo(self, model):
        for nid, x, y, z in self.nodes:
            model.nodes[nid] = Node(nid, x, y, z)
        for i, e in self.elems:
            model.elements.insert(i, Elem(e.id, list(e.nodes), e.config))


class CmdRenumberNode(Command):
    label = "节点重编号"

    def __init__(self, old, new):
        self.old, self.new = old, new

    def redo(self, model):
        n = model.nodes.pop(self.old)
        n.id = self.new
        model.nodes[self.new] = n
        for e in model.elements:
            e.nodes = [self.new if nd == self.old else nd for nd in e.nodes]

    def undo(self, model):
        n = model.nodes.pop(self.new)
        n.id = self.old
        model.nodes[self.old] = n
        for e in model.elements:
            e.nodes = [self.old if nd == self.new else nd for nd in e.nodes]


class CmdRenumberElements(Command):
    label = "单元重编号"

    def __init__(self, old, new):
        self.old, self.new = old, new

    def redo(self, model):
        for e in model.elements:
            if e.id == self.old:
                e.id = self.new

    def undo(self, model):
        for e in model.elements:
            if e.id == self.new:
                e.id = self.old


class CmdFlipElements(Command):
    label = "翻转单元法向"

    def __init__(self, indices):
        self.indices = list(indices)

    def redo(self, model):
        for i in self.indices:
            model.elements[i].nodes.reverse()

    def undo(self, model):
        for i in self.indices:
            model.elements[i].nodes.reverse()


class EditableModel:
    """HMModel 的可编辑包装: 节点字典 + 单元列表 + 命令撤销栈."""

    def __init__(self, model=None, source_path=""):
        model = model or HMModel()
        self.nodes = dict(model.nodes)
        self.elements = [Elem(e.id, list(e.nodes), e.config, comp=e.comp)
                         for e in model.elements]
        self.display_points = dict(model.display_points)
        self.geo_points = dict(model.geo_points)
        self.db_version = model.db_version
        self.element_variant = model.element_variant
        self.comps = dict(model.comps)     # M3.3 collector 数据随包装传递
        self.mats = dict(model.mats)
        self.props = dict(model.props)
        self.groups = dict(model.groups)
        self.others = list(model.others)   # [(id, name)] 文件序, 不按 id 合并
        self.source_path = source_path
        self.undo_stack = []
        self.redo_stack = []
        self.dirty = False

    # ---------------- 查询 ----------------
    def comp_groups(self):
        return Counter(e.comp for e in self.elements if e.comp)

    def config_groups(self):
        return Counter(e.config for e in self.elements)

    def elements_of_nodes(self, nids):
        ns = set(nids)
        return [i for i, e in enumerate(self.elements)
                if any(nd in ns for nd in e.nodes)]

    def elem_centroid(self, e):
        pts = [self.nodes.get(n) for n in e.nodes]
        pts = [p for p in pts if p is not None]
        if not pts:
            return None
        return (sum(p.x for p in pts) / len(pts),
                sum(p.y for p in pts) / len(pts),
                sum(p.z for p in pts) / len(pts))

    def bounds(self):
        if not self.nodes:
            return None
        xs = [n.x for n in self.nodes.values()]
        ys = [n.y for n in self.nodes.values()]
        zs = [n.z for n in self.nodes.values()]
        return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))

    def next_free_node_id(self):
        return (max(self.nodes) + 1) if self.nodes else 1

    def next_free_elem_id(self):
        return (max((e.id for e in self.elements), default=0) + 1)

    # ---------------- 撤销/重做 ----------------
    def apply(self, cmd):
        cmd.redo(self)
        self.undo_stack.append(cmd)
        if len(self.undo_stack) > 200:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self.dirty = True

    def undo(self):
        if not self.undo_stack:
            return None
        cmd = self.undo_stack.pop()
        cmd.undo(self)
        self.redo_stack.append(cmd)
        self.dirty = True
        return cmd

    def redo(self):
        if not self.redo_stack:
            return None
        cmd = self.redo_stack.pop()
        cmd.redo(self)
        self.undo_stack.append(cmd)
        self.dirty = True
        return cmd

    # ---------------- 转换/持久化 ----------------
    def to_hmmodel(self):
        return HMModel(nodes=self.nodes, elements=self.elements,
                       display_points=self.display_points,
                       geo_points=self.geo_points,
                       db_version=self.db_version,
                       node_count=len(self.nodes),
                       elem_count=len(self.elements),
                       element_variant=self.element_variant,
                       comps=self.comps, mats=self.mats, props=self.props,
                       groups=self.groups, others=self.others)

    def to_dict(self):
        return {
            "app": "hm_gui", "format_version": 1,
            "db_version": self.db_version,
            "element_variant": self.element_variant,
            "source": self.source_path,
            "nodes": [[n.id, n.x, n.y, n.z]
                      for n in sorted(self.nodes.values(), key=lambda v: v.id)],
            "elements": [[e.id, e.config, list(e.nodes), e.comp]
                         for e in self.elements],
            "display_points": [[p.id, p.x, p.y, p.z]
                               for p in self.display_points.values()],
            "geo_points": [[p.id, p.x, p.y, p.z]
                           for p in self.geo_points.values()],
            "comps": self.comps, "mats": self.mats,
            "props": self.props, "groups": self.groups,
            "others": [[i, n] for i, n in self.others],
        }

    def save_json(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f)
        self.dirty = False

    @classmethod
    def from_json(cls, path):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        m = HMModel(db_version=d.get("db_version", 0.0),
                    element_variant=d.get("element_variant", "hmj"))
        m.nodes = {int(r[0]): Node(int(r[0]), float(r[1]), float(r[2]), float(r[3]))
                   for r in d.get("nodes", [])}
        m.elements = [Elem(int(r[0]), [int(v) for v in r[2]], int(r[1]),
                           comp=int(r[3]) if len(r) > 3 else 0)
                      for r in d.get("elements", [])]
        m.display_points = {int(r[0]): DisplayPoint(int(r[0]), float(r[1]), float(r[2]), float(r[3]))
                            for r in d.get("display_points", [])}
        m.geo_points = {int(r[0]): GeoPoint(int(r[0]), float(r[1]), float(r[2]), float(r[3]))
                        for r in d.get("geo_points", [])}
        m.comps = {int(k): v for k, v in d.get("comps", {}).items()}
        m.mats = {int(k): v for k, v in d.get("mats", {}).items()}
        m.props = {int(k): v for k, v in d.get("props", {}).items()}
        m.groups = {int(k): v for k, v in d.get("groups", {}).items()}
        m.others = [(int(r[0]), r[1]) for r in d.get("others", [])]
        m.node_count = len(m.nodes)
        m.elem_count = len(m.elements)
        em = cls(m, source_path=d.get("source", ""))
        em.dirty = False
        return em


# ---------------------------------------------------------------------------
# VTK 场景桥: 模型 -> vtkUnstructuredGrid / vtkPolyData
# ---------------------------------------------------------------------------
def _i64(array_like):
    return numpy_to_vtk(np.asarray(array_like, dtype=np.int64), deep=True)


def _u8(array_like):
    return numpy_to_vtk(np.asarray(array_like, dtype=np.uint8), deep=True)


def _parse_id_list(text):
    """解析 "1,3,5-12,7" / "100 - 103" 形式的 id 列表为 set[int].

    支持逗号/空白分隔, '-' 表示闭区间. 非法 token 静默忽略.
    用于节点/单元/几何点 id 选择对话框 (HyperMesh 风格: panel input).
    """
    out = set()
    # 先把两侧带空格的 '-' 归一化为紧凑 'a-b', 避免 split 后出现孤立 '-' token.
    norm = re.sub(r"\s*-\s*", "-", text.strip())
    for tok in re.split(r"[\s,]+", norm):
        if not tok:
            continue
        if tok.startswith("-") or tok.endswith("-"):
            # 单边范围 (例如 "-5", "10-") 视为非法.
            continue
        if "-" in tok:
            try:
                a, b = tok.split("-", 1)
                a, b = int(a), int(b)
                if a > b:
                    a, b = b, a
                out.update(range(a, b + 1))
            except ValueError:
                continue
        else:
            try:
                out.add(int(tok))
            except ValueError:
                continue
    return out


def make_cell_array(cells):
    """cells: list[list[int]] -> vtkCellArray.

    VTK9 的 vtkCellArray.SetData 要求 offsets 数组长度为 nCells+1 且首元素为 0.
    """
    offsets = [0]
    conn = []
    off = 0
    for c in cells:
        conn.extend(c)
        off += len(c)
        offsets.append(off)
    ca = vtk.vtkCellArray()
    ca.SetData(_i64(offsets), _i64(conn))
    return ca


def build_group_grid(vpts, nid2idx, indexed_elems):
    """按 config 分组构建 vtkUnstructuredGrid.

    indexed_elems: [(elem_index, Elem)]
    返回 (grid, n_skipped); 单元数据数组 elem_idx 记录模型单元索引 (拾取用).
    变长 1D (RIGIDLINK/RBE3 等 >2 节点) 扇形展开为多条 LINE.
    """
    cells = []
    types = []
    idx_arr = []
    skipped = 0
    for eidx, e in indexed_elems:
        try:
            ptids = [nid2idx[n] for n in e.nodes]
        except KeyError:
            skipped += 1
            continue
        ct = vtk_cell_type(e.config, len(ptids))
        if ct is None:
            for j in range(1, len(ptids)):
                cells.append([ptids[0], ptids[j]])
                types.append(vtk.VTK_LINE)
                idx_arr.append(eidx)
            continue
        cells.append(ptids)
        types.append(ct)
        idx_arr.append(eidx)
    grid = vtk.vtkUnstructuredGrid()
    grid.SetPoints(vpts)
    if cells:
        grid.SetCells(_u8(types), make_cell_array(cells))
        ea = _i64(idx_arr)
        ea.SetName("elem_idx")
        grid.GetCellData().AddArray(ea)
    return grid, skipped


def build_node_cloud(vpts, nids):
    """节点云 vtkPolyData (VERTS); 单元数据 nid 记录节点 id."""
    pd = vtk.vtkPolyData()
    pd.SetPoints(vpts)
    n = len(nids)
    if n:
        ca = vtk.vtkCellArray()
        ca.SetData(_i64(np.arange(0, n + 1)), _i64(np.arange(n)))
        pd.SetVerts(ca)
        na = _i64(nids)
        na.SetName("nid")
        pd.GetCellData().AddArray(na)
    return pd


def build_points_poly(points):
    """显示点/几何点 -> vtkPolyData (VERTS); 返回 (polydata, [id])."""
    ids = sorted(points)
    pts = np.array([[points[i].x, points[i].y, points[i].z] for i in ids],
                   dtype=float) if ids else np.zeros((0, 3))
    pd = vtk.vtkPolyData()
    vpts = vtk.vtkPoints()
    vpts.SetData(numpy_to_vtk(pts, deep=True))
    pd.SetPoints(vpts)
    n = len(ids)
    if n:
        ca = vtk.vtkCellArray()
        ca.SetData(_i64(np.arange(0, n + 1)), _i64(np.arange(n)))
        pd.SetVerts(ca)
    return pd, ids


class GroupView:
    """一个 config 分组的 VTK 视图对象集."""

    def __init__(self, config, grid, color):
        self.config = config
        self.grid = grid
        self.surface = vtk.vtkDataSetSurfaceFilter()
        self.surface.SetInputData(grid)
        try:
            self.surface.SetNonlinearSubdivisionLevel(1)
        except Exception:
            pass
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.surface.GetOutputPort())
        self.mapper.ScalarVisibilityOff()
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)
        self.actor.GetProperty().SetColor(*color)
        self.actor.GetProperty().SetEdgeColor(0.1, 0.1, 0.1)
        self.actor.GetProperty().SetLineWidth(1.5)
        self.actor.GetProperty().SetPointSize(4)
        self.visible = True


# ---------------------------------------------------------------------------
# 后台加载线程 (大文件解码不卡 UI)
# ---------------------------------------------------------------------------
class LoaderThread(QThread):
    loaded = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path

    def run(self):
        try:
            t0 = time.time()
            model = decode(self.path)
            model._load_seconds = time.time() - t0  # noqa: SLF001
            self.loaded.emit(model)
        except Exception:
            self.failed.emit(traceback.format_exc())


# ---------------------------------------------------------------------------
# 对话框
# ---------------------------------------------------------------------------
class MoveNodeDialog(QDialog):
    """移动节点: 单节点支持绝对/增量, 多节点仅增量."""

    def __init__(self, parent, model, nids):
        super().__init__(parent)
        self.setWindowTitle("移动节点")
        self.model = model
        self.nids = sorted(nids)
        form = QFormLayout(self)
        self.edits = []
        multi = len(self.nids) > 1
        if multi:
            form.addRow(QLabel(f"对 {len(self.nids)} 个节点施加位移增量:"))
        self.rb_abs = QRadioButton("绝对坐标")
        self.rb_rel = QRadioButton("相对增量")
        if not multi:
            hb = QHBoxLayout()
            hb.addWidget(self.rb_abs)
            hb.addWidget(self.rb_rel)
            form.addRow(hb)
            self.rb_abs.setChecked(True)
        else:
            self.rb_abs.setVisible(False)
            self.rb_rel.setChecked(True)
            self.rb_rel.setVisible(False)
        first = model.nodes.get(self.nids[0]) if self.nids else None
        cur = (first.x, first.y, first.z) if (first and not multi) else (0.0, 0.0, 0.0)
        for axis, val in zip("XYZ", cur):
            sp = QDoubleSpinBox()
            sp.setRange(-1e12, 1e12)
            sp.setDecimals(6)
            sp.setValue(val)
            form.addRow(f"{axis}:", sp)
            self.edits.append(sp)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        form.addRow(bb)

    def command(self):
        vals = [e.value() for e in self.edits]
        moves = []
        if self.rb_abs.isChecked() and len(self.nids) == 1:
            nid = self.nids[0]
            n = self.model.nodes[nid]
            moves.append((nid, (n.x, n.y, n.z), tuple(vals)))
        else:
            dx, dy, dz = vals
            for nid in self.nids:
                n = self.model.nodes.get(nid)
                if n is not None:
                    moves.append((nid, (n.x, n.y, n.z),
                                  (n.x + dx, n.y + dy, n.z + dz)))
        return CmdMoveNodes(moves) if moves else None

class TransformDialog(QDialog):
    """节点几何变换: 平移 / 绕轴旋转 / 缩放 / 平面镜像. 复用 CmdMoveNodes 支持撤销."""

    def __init__(self, parent, model, nids, mode):
        super().__init__(parent)
        self.model = model
        self.nids = sorted(nids)
        self.mode = mode
        title = {"translate": "平移节点", "rotate": "旋转节点",
                 "scale": "缩放节点", "reflect": "镜像节点"}[mode]
        self.setWindowTitle(title)
        form = QFormLayout(self)
        form.addRow(QLabel(f"对 {len(self.nids)} 个节点施加「{title}」:"))
        self._f = {}
        def add(name, val=0.0, rng=(-1e12, 1e12), dec=6):
            sp = QDoubleSpinBox()
            sp.setRange(*rng)
            sp.setDecimals(dec)
            sp.setValue(val)
            self._f[name] = sp
            form.addRow(name, sp)
            return sp
        if mode in ("translate",):
            for a in "XYZ":
                add(f"d{a}")
        elif mode == "rotate":
            self.cb_axis = QComboBox()
            self.cb_axis.addItems(["绕 X 轴", "绕 Y 轴", "绕 Z 轴"])
            form.addRow("轴:", self.cb_axis)
            add("px"); add("py"); add("pz")
            add("angle", 0.0, (-36000, 36000), 3)
        elif mode == "scale":
            add("cx"); add("cy"); add("cz")
            add("sx", 1.0, (0.000001, 1e6)); add("sy", 1.0, (0.000001, 1e6)); add("sz", 1.0, (0.000001, 1e6))
        elif mode == "reflect":
            self.cb_plane = QComboBox()
            self.cb_plane.addItems(["X=0 平面", "Y=0 平面", "Z=0 平面"])
            form.addRow("镜像平面:", self.cb_plane)
            add("px"); add("py"); add("pz")
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        form.addRow(bb)

    @staticmethod
    def _rotate(p, axis, ang, center):
        import math
        a = math.radians(ang)
        c, s = math.cos(a), math.sin(a)
        x, y, z = p[0] - center[0], p[1] - center[1], p[2] - center[2]
        if axis == 0:   # X
            y, z = y * c - z * s, y * s + z * c
        elif axis == 1: # Y
            z, x = z * c - x * s, z * s + x * c
        else:           # Z
            x, y = x * c - y * s, x * s + y * c
        return (x + center[0], y + center[1], z + center[2])

    def command(self):
        import math
        moves = []
        for nid in self.nids:
            n = self.model.nodes.get(nid)
            if n is None:
                continue
            old = (n.x, n.y, n.z)
            if self.mode == "translate":
                new = (n.x + self._f["dx"].value(), n.y + self._f["dy"].value(),
                       n.z + self._f["dz"].value())
            elif self.mode == "rotate":
                axis = self.cb_axis.currentIndex()
                center = (self._f["px"].value(), self._f["py"].value(), self._f["pz"].value())
                new = self._rotate(old, axis, self._f["angle"].value(), center)
            elif self.mode == "scale":
                cx, cy, cz = self._f["cx"].value(), self._f["cy"].value(), self._f["cz"].value()
                sx, sy, sz = self._f["sx"].value(), self._f["sy"].value(), self._f["sz"].value()
                new = (cx + (n.x - cx) * sx, cy + (n.y - cy) * sy, cz + (n.z - cz) * sz)
            else:  # reflect
                pl = self.cb_plane.currentIndex()
                px, py, pz = self._f["px"].value(), self._f["py"].value(), self._f["pz"].value()
                if pl == 0:
                    new = (2 * px - n.x, n.y, n.z)
                elif pl == 1:
                    new = (n.x, 2 * py - n.y, n.z)
                else:
                    new = (n.x, n.y, 2 * pz - n.z)
            if new != old:
                moves.append((nid, old, new))
        return CmdMoveNodes(moves) if moves else None


class AddNodeDialog(QDialog):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.setWindowTitle("添加节点")
        form = QFormLayout(self)
        self.id_edit = QSpinBox()
        self.id_edit.setRange(1, 10_000_000)
        self.id_edit.setValue(model.next_free_node_id())
        form.addRow("节点 ID:", self.id_edit)
        self.xyz = []
        for axis in "XYZ":
            sp = QDoubleSpinBox()
            sp.setRange(-1e12, 1e12)
            sp.setDecimals(6)
            form.addRow(f"{axis}:", sp)
            self.xyz.append(sp)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        form.addRow(bb)

    def values(self):
        return self.id_edit.value(), tuple(sp.value() for sp in self.xyz)


class AddElementDialog(QDialog):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.setWindowTitle("添加单元")
        form = QFormLayout(self)
        self.id_edit = QSpinBox()
        self.id_edit.setRange(1, 100_000_000)
        self.id_edit.setValue(model.next_free_elem_id())
        form.addRow("单元 ID:", self.id_edit)
        self.cfg = QComboBox()
        for c in sorted(CONFIG_TABLE):
            name, nn, cat = CONFIG_TABLE[c]
            self.cfg.addItem(f"{c} {name} [{cat}] ({nn or '变长'}节点)", c)
        self.cfg.setCurrentText("103 TRIA3 [2D] (3节点)")
        form.addRow("Config:", self.cfg)
        self.nodes_edit = QLineEdit()
        self.nodes_edit.setPlaceholderText("节点 id, 空格/逗号分隔, 如: 101 102 103")
        form.addRow("节点:", self.nodes_edit)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        form.addRow(bb)

    def values(self):
        cfg = self.cfg.currentData()
        ids = [int(t) for t in self.nodes_edit.text()
               .replace(",", " ").split() if t]
        return self.id_edit.value(), cfg, ids


class RenumberDialog(QDialog):
    def __init__(self, parent, title, old=0, new=1):
        super().__init__(parent)
        self.setWindowTitle(title)
        form = QFormLayout(self)
        self.old = QSpinBox()
        self.old.setRange(1, 100_000_000)
        self.old.setValue(max(1, old))
        self.new = QSpinBox()
        self.new.setRange(1, 100_000_000)
        self.new.setValue(max(1, new))
        form.addRow("旧 ID:", self.old)
        form.addRow("新 ID:", self.new)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        form.addRow(bb)

    def values(self):
        return self.old.value(), self.new.value()


class SelectByIdDialog(QDialog):
    """按 ID 选择: 支持 '1 2 3', '1,2,3', '10-50' 区间; 模式 替换/添加/减去."""

    def __init__(self, parent, target):
        super().__init__(parent)
        self.setWindowTitle(f"按 ID 选择{target}")
        self.target = target
        form = QFormLayout(self)
        self.ids_edit = QLineEdit()
        self.ids_edit.setPlaceholderText("如: 1 2 3 或 10-100")
        form.addRow(f"{target} ID:", self.ids_edit)
        self.mode = QComboBox()
        self.mode.addItems(["替换选择", "添加到选择", "从选择减去"])
        form.addRow("模式:", self.mode)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        form.addRow(bb)

    @staticmethod
    def parse_ids(text):
        out = set()
        for tok in text.replace(",", " ").split():
            if "-" in tok[1:]:
                a, b = tok.split("-", 1)
                try:
                    out.update(range(int(a), int(b) + 1))
                    continue
                except ValueError:
                    pass
            try:
                out.add(int(tok))
            except ValueError:
                pass
        return out

    def values(self):
        return self.parse_ids(self.ids_edit.text()), self.mode.currentIndex()


class HmView(QVTKRenderWindowInteractor):
    """QVTK 视图, 在 Qt 层转发鼠标事件.

    注意: vtkInteractorStyleTrackballCamera.OnLeftButtonDown 会调用
    GrabFocus(EventCallbackCommand), 之后 vtkObject.InvokeEvent 的
    "focus loop" 只把 LeftButtonReleaseEvent / 拖动期间的 MouseMoveEvent
    派发给样式本身, 普通 AddObserver 观察者永远收不到 release 事件.
    因此在 Qt 控件层 (mousePressEvent/mouseReleaseEvent/mouseMoveEvent)
    截取鼠标事件, 通过信号转发给主窗口, 完全绕开 VTK 焦点机制.
    坐标统一从 interactor.GetEventPosition() 读取 (已做 y 翻转),
    与 vtkCellPicker.Pick 的显示坐标系一致.
    """

    sig_press = pyqtSignal()
    sig_release = pyqtSignal()
    sig_move = pyqtSignal()

    def mousePressEvent(self, ev):
        super().mousePressEvent(ev)
        if ev.button() == Qt.LeftButton:
            self.sig_press.emit()

    def mouseReleaseEvent(self, ev):
        super().mouseReleaseEvent(ev)
        if ev.button() == Qt.LeftButton:
            self.sig_release.emit()

    def mouseMoveEvent(self, ev):
        super().mouseMoveEvent(ev)
        self.sig_move.emit()


class HmIcons:
    """矢量图标工厂 (参考 pphdecoding AppIcons): 工具栏 / 模型树 / 视口条共用缓存."""

    _cache = {}
    _FOLDER = {
        "folder_asm": ("#e8a317", "#ffd966", "#8a5a00"),
        "folder_comp": ("#2e75b6", "#5b9bd5", "#1f4e79"),
        "folder_mat": ("#43a047", "#81c784", "#1b5e20"),
        "folder_prop": ("#f9a825", "#ffe082", "#f57f17"),
        "folder_set": ("#8e24aa", "#ce93d8", "#4a148c"),
        "folder_grp": ("#00897b", "#80cbc4", "#004d40"),
        "folder_load": ("#e53935", "#ef9a9a", "#b71c1c"),
        "folder_sys": ("#607d8b", "#b0bec5", "#37474f"),
        "folder_vec": ("#00acc1", "#80deea", "#006064"),
        "folder_other": ("#8d6e63", "#d7ccc8", "#4e342e"),
        "folder_title": ("#eceff1", "#ffffff", "#78909c"),
        "folder_nodes": ("#1565c0", "#90caf9", "#0d47a1"),
        "folder_elems": ("#ad1457", "#f48fb1", "#880e4f"),
        "folder_geo": ("#6d4c41", "#bcaaa4", "#3e2723"),
    }

    @classmethod
    def get(cls, name, size=20):
        key = (name, size)
        if key not in cls._cache:
            cls._cache[key] = QIcon(cls._paint(name, size))
        return cls._cache[key]

    @classmethod
    def swatch(cls, rgb, size=16):
        key = ("swatch", tuple(round(float(c), 4) for c in rgb[:3]), size)
        if key not in cls._cache:
            pm = QPixmap(size, size)
            pm.fill(Qt.transparent)
            p = QPainter(pm)
            p.setRenderHint(QPainter.Antialiasing)
            m = max(2, size // 8)
            p.setPen(QPen(QColor("#333333"), 1))
            p.setBrush(QBrush(QColor.fromRgbF(*rgb[:3])))
            p.drawRoundedRect(m, m, size - 2 * m, size - 2 * m, 2, 2)
            p.end()
            cls._cache[key] = QIcon(pm)
        return cls._cache[key]

    @classmethod
    def _paint(cls, name, size):
        pm = QPixmap(size, size)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing, True)
        m = max(1, size // 10)
        r = QRectF(m, m, size - 2 * m, size - 2 * m)
        if name in cls._FOLDER:
            tab, body, edge = cls._FOLDER[name]
            cls._draw_folder(p, r, tab, body, edge)
        else:
            drawer = getattr(cls, f"_draw_{name}", None)
            if drawer:
                drawer(p, r, size)
            else:
                cls._draw_generic(p, r, size)
        p.end()
        return pm

    @staticmethod
    def _pen(color, w=1.5):
        pen = QPen(QColor(color))
        pen.setWidthF(w)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setCapStyle(Qt.RoundCap)
        return pen

    @classmethod
    def _draw_folder(cls, p, r, tab, body, edge):
        p.setPen(cls._pen(edge, 1.15))
        p.setBrush(QBrush(QColor(tab)))
        p.drawRoundedRect(QRectF(r.left(), r.top(), r.width() * 0.46,
                                 r.height() * 0.30), 1.4, 1.4)
        p.setBrush(QBrush(QColor(body)))
        p.drawRoundedRect(QRectF(r.left(), r.top() + r.height() * 0.22,
                                 r.width(), r.height() * 0.70), 1.6, 1.6)

    @classmethod
    def _draw_generic(cls, p, r, _s=0):
        p.setPen(cls._pen("#555"))
        p.setBrush(QBrush(QColor("#dde3ea")))
        p.drawRoundedRect(r, 3, 3)

    @classmethod
    def _draw_new(cls, p, r, _s):
        p.setPen(cls._pen("#37474f", 1.3))
        p.setBrush(QBrush(QColor("#fff")))
        p.drawRoundedRect(r, 1.5, 1.5)
        p.setBrush(QBrush(QColor("#eceff1")))
        fold = QPolygon([
            QPoint(int(r.right() - r.width() * 0.38), int(r.top())),
            QPoint(int(r.right()), int(r.top() + r.height() * 0.38)),
            QPoint(int(r.right() - r.width() * 0.38),
                   int(r.top() + r.height() * 0.38)),
        ])
        p.drawPolygon(fold)

    @classmethod
    def _draw_open(cls, p, r, _s):
        cls._draw_folder(p, r, "#f4c542", "#ffd966", "#2e75b6")

    @classmethod
    def _draw_save(cls, p, r, _s):
        p.setPen(cls._pen("#1f4e79", 1.2))
        p.setBrush(QBrush(QColor("#5b9bd5")))
        p.drawRoundedRect(r, 2, 2)
        p.setBrush(QBrush(QColor("#fff")))
        p.drawRect(QRectF(r.left() + r.width() * 0.22, r.top(),
                          r.width() * 0.56, r.height() * 0.36))
        p.setBrush(QBrush(QColor("#eaf2fb")))
        p.drawRoundedRect(QRectF(r.left() + r.width() * 0.18,
                                 r.top() + r.height() * 0.48,
                                 r.width() * 0.64, r.height() * 0.40), 1, 1)

    @classmethod
    def _draw_print(cls, p, r, _s):
        p.setPen(cls._pen("#455a64", 1.2))
        p.setBrush(QBrush(QColor("#90a4ae")))
        p.drawRoundedRect(QRectF(r.left(), r.top() + r.height() * 0.28,
                                 r.width(), r.height() * 0.42), 2, 2)
        p.setBrush(QBrush(QColor("#fff")))
        p.drawRect(QRectF(r.left() + r.width() * 0.22, r.top(),
                          r.width() * 0.56, r.height() * 0.34))
        p.drawRect(QRectF(r.left() + r.width() * 0.18,
                          r.top() + r.height() * 0.58,
                          r.width() * 0.64, r.height() * 0.34))

    @classmethod
    def _draw_undo(cls, p, r, _s):
        p.setPen(cls._pen("#1565c0", 2.0))
        p.setBrush(Qt.NoBrush)
        p.drawArc(r.toRect(), 40 * 16, 250 * 16)
        cx, cy = r.center().x(), r.center().y()
        tip = QPolygon([
            QPoint(int(r.left()), int(cy)),
            QPoint(int(r.left() + r.width() * 0.32), int(cy - r.height() * 0.28)),
            QPoint(int(r.left() + r.width() * 0.32), int(cy + r.height() * 0.08)),
        ])
        p.setBrush(QBrush(QColor("#1565c0")))
        p.setPen(Qt.NoPen)
        p.drawPolygon(tip)

    @classmethod
    def _draw_redo(cls, p, r, _s):
        p.setPen(cls._pen("#1565c0", 2.0))
        p.setBrush(Qt.NoBrush)
        p.drawArc(r.toRect(), 250 * 16, 250 * 16)
        cx, cy = r.center().x(), r.center().y()
        tip = QPolygon([
            QPoint(int(r.right()), int(cy)),
            QPoint(int(r.right() - r.width() * 0.32), int(cy - r.height() * 0.28)),
            QPoint(int(r.right() - r.width() * 0.32), int(cy + r.height() * 0.08)),
        ])
        p.setBrush(QBrush(QColor("#1565c0")))
        p.setPen(Qt.NoPen)
        p.drawPolygon(tip)

    @classmethod
    def _draw_fit(cls, p, r, _s):
        p.setPen(cls._pen("#37474f", 1.6))
        p.setBrush(Qt.NoBrush)
        s = r.width() * 0.28
        for x, y, sx, sy in (
            (r.left(), r.top(), 1, 1), (r.right(), r.top(), -1, 1),
            (r.left(), r.bottom(), 1, -1), (r.right(), r.bottom(), -1, -1),
        ):
            p.drawLine(QPoint(int(x), int(y)), QPoint(int(x + sx * s), int(y)))
            p.drawLine(QPoint(int(x), int(y)), QPoint(int(x), int(y + sy * s)))
        p.setBrush(QBrush(QColor("#90a4ae")))
        p.drawEllipse(r.adjusted(r.width() * 0.28, r.height() * 0.28,
                                 -r.width() * 0.28, -r.height() * 0.28))

    @classmethod
    def _draw_rotate(cls, p, r, _s):
        p.setPen(cls._pen("#6a1b9a", 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(r.adjusted(2, 2, -2, -2))
        p.drawLine(QPoint(int(r.center().x()), int(r.top() + 2)),
                   QPoint(int(r.center().x()), int(r.center().y())))
        p.setBrush(QBrush(QColor("#8e24aa")))
        p.drawEllipse(QRectF(r.center().x() - 2, r.center().y() - 2, 4, 4))

    @classmethod
    def _draw_pan(cls, p, r, _s):
        p.setPen(cls._pen("#37474f", 1.5))
        cx, cy = int(r.center().x()), int(r.center().y())
        p.drawLine(QPoint(int(r.left()), cy), QPoint(int(r.right()), cy))
        p.drawLine(QPoint(cx, int(r.top())), QPoint(cx, int(r.bottom())))

    @classmethod
    def _draw_zoom(cls, p, r, _s):
        p.setPen(cls._pen("#1565c0", 1.4))
        p.setBrush(QBrush(QColor("#bbdefb")))
        p.drawEllipse(r.adjusted(0, 0, -r.width() * 0.22, -r.height() * 0.22))
        p.setPen(cls._pen("#1565c0", 2.0))
        p.drawLine(QPoint(int(r.right() - r.width() * 0.28),
                          int(r.bottom() - r.height() * 0.28)),
                   QPoint(int(r.right()), int(r.bottom())))

    @classmethod
    def _draw_box(cls, p, r, _s):
        pen = cls._pen("#2e7d32", 1.3)
        pen.setStyle(Qt.DashLine)
        p.setPen(pen)
        p.setBrush(QBrush(QColor(46, 125, 50, 40)))
        p.drawRect(r.adjusted(1, 2, -1, -2))

    @classmethod
    def _draw_shaded(cls, p, r, _s):
        p.setPen(cls._pen("#1a237e", 1.2))
        p.setBrush(QBrush(QColor("#c2185b")))
        p.drawPolygon(QPolygon([
            QPoint(int(r.left()), int(r.bottom())),
            QPoint(int(r.center().x()), int(r.top())),
            QPoint(int(r.right()), int(r.bottom())),
        ]))

    @classmethod
    def _draw_wire(cls, p, r, _s):
        p.setPen(cls._pen("#1a237e", 1.2))
        p.setBrush(Qt.NoBrush)
        pts = QPolygon([
            QPoint(int(r.left()), int(r.bottom())),
            QPoint(int(r.center().x()), int(r.top())),
            QPoint(int(r.right()), int(r.bottom())),
        ])
        p.drawPolygon(pts)
        p.drawLine(QPoint(int(r.center().x()), int(r.top())),
                   QPoint(int(r.center().x()), int(r.bottom())))

    @classmethod
    def _draw_hidden(cls, p, r, _s):
        p.setPen(cls._pen("#455a64", 1.2))
        p.setBrush(QBrush(QColor("#b0bec5")))
        p.drawPolygon(QPolygon([
            QPoint(int(r.left()), int(r.bottom())),
            QPoint(int(r.center().x()), int(r.top())),
            QPoint(int(r.right()), int(r.bottom())),
        ]))
        p.setPen(cls._pen("#eceff1", 1.4))
        p.drawLine(QPoint(int(r.left() + 2), int(r.bottom() - 3)),
                   QPoint(int(r.right() - 2), int(r.bottom() - 3)))

    @classmethod
    def _draw_points(cls, p, r, _s):
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor("#1565c0")))
        for fx, fy in ((0.25, 0.28), (0.72, 0.32), (0.48, 0.70)):
            p.drawEllipse(QPointF(r.left() + r.width() * fx,
                                  r.top() + r.height() * fy), 2.2, 2.2)

    @classmethod
    def _draw_del(cls, p, r, _s):
        p.setPen(cls._pen("#c62828", 2.0))
        p.drawLine(QPoint(int(r.left() + 1), int(r.top() + 1)),
                   QPoint(int(r.right() - 1), int(r.bottom() - 1)))
        p.drawLine(QPoint(int(r.right() - 1), int(r.top() + 1)),
                   QPoint(int(r.left() + 1), int(r.bottom() - 1)))

    @classmethod
    def _draw_help(cls, p, r, _s):
        p.setPen(cls._pen("#1565c0", 1.3))
        p.setBrush(QBrush(QColor("#bbdefb")))
        p.drawEllipse(r)
        p.setPen(cls._pen("#0d47a1", 1.2))
        p.setFont(QFont("Segoe UI", max(7, int(r.height() * 0.55)), QFont.Bold))
        p.drawText(r.toRect(), Qt.AlignCenter, "?")

    @classmethod
    def _draw_find(cls, p, r, _s):
        cls._draw_zoom(p, r, _s)

    @classmethod
    def _draw_mask(cls, p, r, _s):
        p.setPen(cls._pen("#6d4c41", 1.2))
        p.setBrush(QBrush(QColor("#d7ccc8")))
        p.drawRoundedRect(r, 2, 2)
        p.setBrush(QBrush(QColor("#8d6e63")))
        p.drawRect(QRectF(r.left(), r.top(), r.width() * 0.45, r.height()))

    @classmethod
    def _draw_isolate(cls, p, r, _s):
        p.setPen(cls._pen("#ef6c00", 1.2))
        p.setBrush(QBrush(QColor("#ffe0b2")))
        p.drawEllipse(r)
        p.setBrush(QBrush(QColor("#ef6c00")))
        p.drawEllipse(r.adjusted(r.width() * 0.28, r.height() * 0.28,
                                 -r.width() * 0.28, -r.height() * 0.28))

    @classmethod
    def _draw_numbers(cls, p, r, _s):
        p.setPen(cls._pen("#37474f", 1.1))
        p.setBrush(QBrush(QColor("#fff9c4")))
        p.drawRoundedRect(r, 2, 2)
        p.setFont(QFont("Segoe UI", max(6, int(r.height() * 0.5)), QFont.Bold))
        p.drawText(r.toRect(), Qt.AlignCenter, "12")

    @classmethod
    def _draw_count(cls, p, r, _s):
        p.setPen(cls._pen("#1565c0", 1.1))
        p.setBrush(QBrush(QColor("#e3f2fd")))
        p.drawRoundedRect(r, 2, 2)
        p.setFont(QFont("Segoe UI", max(6, int(r.height() * 0.45)), QFont.Bold))
        p.drawText(r.toRect(), Qt.AlignCenter, "N")

    @classmethod
    def _draw_front(cls, p, r, _s):
        p.setPen(cls._pen("#455a64", 1.2))
        p.setBrush(QBrush(QColor("#90caf9")))
        p.drawRect(r.adjusted(2, 2, -2, -2))

    @classmethod
    def _draw_top(cls, p, r, _s):
        p.setPen(cls._pen("#455a64", 1.2))
        p.setBrush(QBrush(QColor("#a5d6a7")))
        p.drawRect(r.adjusted(1, r.height() * 0.28, -1, -r.height() * 0.28))

    @classmethod
    def _draw_side(cls, p, r, _s):
        p.setPen(cls._pen("#455a64", 1.2))
        p.setBrush(QBrush(QColor("#ffcc80")))
        p.drawRect(r.adjusted(r.width() * 0.28, 1, -r.width() * 0.28, -1))

    @classmethod
    def _draw_iso(cls, p, r, _s):
        p.setPen(cls._pen("#37474f", 1.15))
        p.setBrush(QBrush(QColor("#90caf9")))
        cx, cy = r.center().x(), r.center().y()
        top = QPolygon([
            QPoint(int(cx), int(r.top())),
            QPoint(int(r.right()), int(cy - r.height() * 0.12)),
            QPoint(int(cx), int(cy + r.height() * 0.08)),
            QPoint(int(r.left()), int(cy - r.height() * 0.12)),
        ])
        p.drawPolygon(top)
        p.setBrush(QBrush(QColor("#64b5f6")))
        p.drawPolygon(QPolygon([
            QPoint(int(r.left()), int(cy - r.height() * 0.12)),
            QPoint(int(cx), int(cy + r.height() * 0.08)),
            QPoint(int(cx), int(r.bottom())),
            QPoint(int(r.left()), int(r.bottom() - r.height() * 0.18)),
        ]))
        p.setBrush(QBrush(QColor("#42a5f5")))
        p.drawPolygon(QPolygon([
            QPoint(int(cx), int(cy + r.height() * 0.08)),
            QPoint(int(r.right()), int(cy - r.height() * 0.12)),
            QPoint(int(r.right()), int(r.bottom() - r.height() * 0.18)),
            QPoint(int(cx), int(r.bottom())),
        ]))

    @classmethod
    def _draw_pick(cls, p, r, _s):
        p.setPen(cls._pen("#333", 1.3))
        p.setBrush(QBrush(QColor("#fff")))
        p.drawPolygon(QPolygon([
            QPoint(int(r.left() + 1), int(r.top() + 1)),
            QPoint(int(r.left() + 1), int(r.bottom() - r.height() * 0.15)),
            QPoint(int(r.left() + r.width() * 0.38), int(r.bottom() - r.height() * 0.38)),
            QPoint(int(r.right() - 1), int(r.bottom() - 1)),
        ]))

    @classmethod
    def _draw_section(cls, p, r, _s):
        p.setPen(cls._pen("#455a64", 1.2))
        p.setBrush(QBrush(QColor("#b0bec5")))
        p.drawRoundedRect(r, 2, 2)
        p.setPen(cls._pen("#c62828", 2.0))
        p.drawLine(QPoint(int(r.left()), int(r.top() + r.height() * 0.7)),
                   QPoint(int(r.right()), int(r.top() + r.height() * 0.3)))

    @classmethod
    def _draw_measure(cls, p, r, _s):
        p.setPen(cls._pen("#6a1b9a", 1.4))
        p.drawLine(QPoint(int(r.left()), int(r.bottom() - 2)),
                   QPoint(int(r.right()), int(r.top() + 2)))
        p.drawLine(QPoint(int(r.left()), int(r.bottom() - 5)),
                   QPoint(int(r.left()), int(r.bottom())))
        p.drawLine(QPoint(int(r.right()), int(r.top())),
                   QPoint(int(r.right()), int(r.top() + 5)))

    @classmethod
    def _draw_refresh(cls, p, r, _s):
        p.setPen(cls._pen("#2e7d32", 1.8))
        p.setBrush(Qt.NoBrush)
        p.drawArc(r.toRect(), 50 * 16, 260 * 16)

    @classmethod
    def _draw_filter(cls, p, r, _s):
        p.setPen(cls._pen("#455a64", 1.2))
        p.setBrush(QBrush(QColor("#90a4ae")))
        p.drawPolygon(QPolygon([
            QPoint(int(r.left()), int(r.top() + 1)),
            QPoint(int(r.right()), int(r.top() + 1)),
            QPoint(int(r.center().x() + r.width() * 0.12), int(r.center().y())),
            QPoint(int(r.center().x() + r.width() * 0.12), int(r.bottom())),
            QPoint(int(r.center().x() - r.width() * 0.12), int(r.bottom())),
            QPoint(int(r.center().x() - r.width() * 0.12), int(r.center().y())),
        ]))

    @classmethod
    def _draw_create(cls, p, r, _s):
        p.setPen(cls._pen("#2e7d32", 2.0))
        cx, cy = int(r.center().x()), int(r.center().y())
        p.drawLine(QPoint(int(r.left() + 2), cy), QPoint(int(r.right() - 2), cy))
        p.drawLine(QPoint(cx, int(r.top() + 2)), QPoint(cx, int(r.bottom() - 2)))

    @classmethod
    def _draw_ent_node(cls, p, r, _s):
        p.setPen(cls._pen("#1565c0", 1.2))
        p.setBrush(QBrush(QColor("#42a5f5")))
        p.drawEllipse(r.adjusted(r.width() * 0.22, r.height() * 0.22,
                                 -r.width() * 0.22, -r.height() * 0.22))

    @classmethod
    def _draw_ent_line(cls, p, r, _s):
        p.setPen(cls._pen("#ef6c00", 2.0))
        p.drawLine(QPoint(int(r.left() + 1), int(r.bottom() - 2)),
                   QPoint(int(r.right() - 1), int(r.top() + 2)))

    @classmethod
    def _draw_ent_surf(cls, p, r, _s):
        p.setPen(cls._pen("#2e7d32", 1.2))
        p.setBrush(QBrush(QColor("#81c784")))
        p.drawRoundedRect(r.adjusted(1, 3, -1, -3), 2, 2)

    @classmethod
    def _draw_ent_solid(cls, p, r, _s):
        cls._draw_iso(p, r, _s)

    @classmethod
    def _draw_ent_elem(cls, p, r, _s):
        cls._draw_shaded(p, r, _s)

    @classmethod
    def _draw_color_mode(cls, p, r, _s):
        colors = ("#e91e63", "#2196f3", "#4caf50", "#ff9800")
        cells = (
            QRectF(r.left(), r.top(), r.width() * 0.48, r.height() * 0.48),
            QRectF(r.left() + r.width() * 0.52, r.top(),
                   r.width() * 0.48, r.height() * 0.48),
            QRectF(r.left(), r.top() + r.height() * 0.52,
                   r.width() * 0.48, r.height() * 0.48),
            QRectF(r.left() + r.width() * 0.52, r.top() + r.height() * 0.52,
                   r.width() * 0.48, r.height() * 0.48),
        )
        p.setPen(cls._pen("#455a64", 0.8))
        for cell, c in zip(cells, colors):
            p.setBrush(QBrush(QColor(c)))
            p.drawRoundedRect(cell, 1, 1)

    @classmethod
    def _draw_mesh(cls, p, r, _s):
        p.setPen(cls._pen("#ad1457", 1.15))
        p.setBrush(QBrush(QColor("#f48fb1")))
        p.drawPolygon(QPolygon([
            QPoint(int(r.left()), int(r.bottom())),
            QPoint(int(r.center().x()), int(r.top())),
            QPoint(int(r.right()), int(r.bottom())),
        ]))
        p.drawLine(QPoint(int(r.center().x()), int(r.top())),
                   QPoint(int(r.center().x()), int(r.bottom())))

    @classmethod
    def _draw_leaf_prop(cls, p, r, _s):
        p.setPen(cls._pen("#f9a825", 1.2))
        p.setBrush(QBrush(QColor("#fff59d")))
        p.drawRoundedRect(r, 2, 2)
        p.setPen(cls._pen("#f57f17", 1.1))
        for i in range(3):
            y = r.top() + r.height() * (0.30 + i * 0.22)
            p.drawLine(QPoint(int(r.left() + 3), int(y)),
                       QPoint(int(r.right() - 3), int(y)))

    @classmethod
    def _draw_leaf_mat(cls, p, r, _s):
        p.setPen(cls._pen("#2e7d32", 1.2))
        p.setBrush(QBrush(QColor("#81c784")))
        cx, cy = r.center().x(), r.center().y()
        w, h = r.width() * 0.40, r.height() * 0.40
        p.drawPolygon(QPolygon([
            QPoint(int(cx), int(cy - h)), QPoint(int(cx + w), int(cy)),
            QPoint(int(cx), int(cy + h)), QPoint(int(cx - w), int(cy)),
        ]))

    @classmethod
    def _draw_leaf_title(cls, p, r, _s):
        p.setPen(cls._pen("#78909c", 1.15))
        p.setBrush(QBrush(QColor("#fff")))
        p.drawRoundedRect(r, 1.5, 1.5)
        p.setFont(QFont("Segoe UI", max(6, int(r.height() * 0.5)), QFont.Bold))
        p.setPen(cls._pen("#546e7a", 1.0))
        p.drawText(r.toRect(), Qt.AlignCenter, "T")

    @classmethod
    def _draw_leaf_set(cls, p, r, _s):
        p.setPen(cls._pen("#6a1b9a", 1.2))
        p.setBrush(QBrush(QColor("#ce93d8")))
        p.drawEllipse(r.adjusted(2, 2, -2, -2))

    @classmethod
    def _draw_leaf_load(cls, p, r, _s):
        p.setPen(cls._pen("#b71c1c", 1.3))
        p.setBrush(QBrush(QColor("#ef9a9a")))
        p.drawPolygon(QPolygon([
            QPoint(int(r.center().x()), int(r.top())),
            QPoint(int(r.right()), int(r.bottom() - 1)),
            QPoint(int(r.left()), int(r.bottom() - 1)),
        ]))

    @classmethod
    def _draw_leaf_asm(cls, p, r, _s):
        p.setPen(cls._pen("#e65100", 1.2))
        p.setBrush(QBrush(QColor("#ffcc80")))
        p.drawRoundedRect(r.adjusted(1, 3, -1, -3), 2, 2)

    @classmethod
    def _draw_leaf_node(cls, p, r, _s):
        cls._draw_ent_node(p, r, _s)

    @classmethod
    def _draw_leaf_elem(cls, p, r, _s):
        cls._draw_ent_elem(p, r, _s)

    @classmethod
    def _draw_leaf_disp(cls, p, r, _s):
        p.setPen(cls._pen("#00838f", 1.2))
        p.setBrush(QBrush(QColor("#80deea")))
        p.drawEllipse(r.adjusted(3, 3, -3, -3))

    @classmethod
    def _draw_leaf_geo(cls, p, r, _s):
        p.setPen(cls._pen("#5d4037", 1.4))
        cx, cy = int(r.center().x()), int(r.center().y())
        p.drawLine(QPoint(int(r.left() + 1), cy), QPoint(int(r.right() - 1), cy))
        p.drawLine(QPoint(cx, int(r.top() + 1)), QPoint(cx, int(r.bottom() - 1)))
        p.setBrush(QBrush(QColor("#8d6e63")))
        p.drawEllipse(QRectF(r.center().x() - 2, r.center().y() - 2, 4, 4))


def hm_icon(kind, size=20):
    """兼容入口: 工具栏 / 旧调用走 HmIcons 缓存."""
    return HmIcons.get(kind, size)


FOLDER_ICONS = {
    "Assemblies": "folder_asm", "Components": "folder_comp",
    "Materials": "folder_mat", "Properties": "folder_prop",
    "Sets": "folder_set", "Groups": "folder_grp", "Load": "folder_load",
    "System": "folder_sys", "Vector": "folder_vec", "Others": "folder_other",
    "Titles": "folder_title",
}
LEAF_ICONS = {
    "asm": "leaf_asm", "mat": "leaf_mat", "prop": "leaf_prop",
    "set": "leaf_set", "grp": "leaf_set", "load": "leaf_load",
    "sys": "folder_sys", "vec": "folder_vec", "other": "folder_other",
    "title": "leaf_title",
}


class HmPanelBar(QFrame):
    """HyperMesh 底部 panel area: 左侧按钮栅格 + 右侧 page menu.

    官方说明: 'Pre-processing and post-processing tools are displayed on
    panels located at the bottom of the application.'
    (help/hm/topics/panels/panels_r.htm)
    """

    pageChanged = pyqtSignal(str)
    panelClicked = pyqtSignal(str, str)   # page, panel

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HmPanelBar")
        self.setFixedHeight(168)
        self._page = "Geom"
        self._active = None
        root = QHBoxLayout(self)
        root.setContentsMargins(6, 4, 4, 4)
        root.setSpacing(6)

        left = QVBoxLayout()
        left.setSpacing(3)
        self.sub_label = QLabel("Geom")
        self.sub_label.setStyleSheet("font-weight: bold; color: #234;")
        left.addWidget(self.sub_label)
        self.stack = QStackedWidget()
        self._page_index = {}
        for i, (page, cols) in enumerate(HM_PANEL_PAGES.items()):
            page_w = QWidget()
            grid = QHBoxLayout(page_w)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setSpacing(10)
            for col in cols:
                col_l = QVBoxLayout()
                col_l.setSpacing(3)
                for name in col:
                    btn = QPushButton(name)
                    btn.setObjectName("HmPanelBtn")
                    btn.setFocusPolicy(Qt.NoFocus)
                    btn.clicked.connect(
                        lambda _c=False, pg=page, pn=name: self._on_btn(pg, pn))
                    col_l.addWidget(btn)
                col_l.addStretch(1)
                grid.addLayout(col_l)
            grid.addStretch(1)
            self.stack.addWidget(page_w)
            self._page_index[page] = i
        left.addWidget(self.stack, 1)
        root.addLayout(left, 1)

        pages = QVBoxLayout()
        pages.setSpacing(1)
        pages.addWidget(QLabel("page"))
        self._page_group = QButtonGroup(self)
        for page in HM_PANEL_PAGES:
            rb = QRadioButton(page)
            rb.setObjectName("HmPageRadio")
            rb.setChecked(page == "Geom")
            rb.toggled.connect(lambda on, pg=page: on and self.set_page(pg))
            self._page_group.addButton(rb)
            pages.addWidget(rb)
        pages.addStretch(1)
        root.addLayout(pages)

    def set_page(self, page):
        if page not in self._page_index:
            return
        self._page = page
        self.stack.setCurrentIndex(self._page_index[page])
        self.sub_label.setText(page)
        self.pageChanged.emit(page)

    def _on_btn(self, page, name):
        self._active = name
        self.sub_label.setText(f"{page}  /  {name}")
        self.panelClicked.emit(page, name)


# ---------------------------------------------------------------------------
# 主窗口
# ---------------------------------------------------------------------------
class HmMainWindow(QMainWindow):
    def __init__(self, path=None):
        super().__init__()
        self.setWindowTitle(f"HyperMesh 2019 - {HM_PROFILE_DEFAULT}")
        self.setWindowIcon(HmIcons.get("mesh", 32))
        self.resize(1600, 960)
        self.setAcceptDrops(True)
        self.setStyleSheet(HM_QSS)
        self._user_profile = HM_PROFILE_DEFAULT

        self.model = None              # EditableModel
        self.loader = None
        self._iren_ready = False
        self._startup_redraw = True
        self._display_mode = 1         # 表面+边
        self._pick_target = "元素"      # 元素 | 节点
        self._interact = "旋转"         # 旋转 | 框选
        self._press_pos = None
        self._bg_dark = True           # 默认对齐 HM 2019 深蓝视口
        self._current_page = "Geom"
        self._scale_actor = None
        self._color_mode = "By Comp"

        # VTK 对象
        self._vpts = None              # 共享 vtkPoints
        self._nid2idx = {}
        self._idx2nid = []
        self._groups = {}              # config -> GroupView
        self._group_style = {}         # config -> (color, visible) 跨重建保持
        self._node_actor = None
        self._node_poly = None
        self._disp_actor = None
        self._geo_actor = None
        self._elem_hl_actor = None
        self._node_hl_actor = None
        self._geo_hl_actor = None
        self._orientation = None
        self._anno = None

        # 选择状态: 单元用模型索引, 节点用 id
        self.sel_elems = set()
        self.sel_nodes = set()
        self.sel_geo_points = set()

        self._build_menus()
        self._build_toolbar()
        self._build_workspace()
        self._build_statusbar()
        self._update_edit_actions()

        if path:
            QTimer.singleShot(100, lambda: self.open_path(path))

    # ---------------- UI 构建 ----------------
    def _build_workspace(self):
        """HyperMesh 经典工作区 (workspace_hm_classic_r.htm):

        Tab Area | Modeling Window
                 | Panel Area
        Status Bar
        """
        view_host = QWidget()
        view_host.setObjectName("PaneFrame")
        vl = QVBoxLayout(view_host)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)
        # QVTK 必须直接创建在最终父控件上; 再 SetParent 会丢掉 OpenGL 上下文.
        view_row = QWidget()
        hl = QHBoxLayout(view_row)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(0)
        hl.addWidget(self._build_view_strip())
        self.vtk_widget = HmView(view_row)
        self.vtk_widget.sig_press.connect(self._on_qt_press)
        self.vtk_widget.sig_release.connect(self._on_qt_release)
        self.vtk_widget.sig_move.connect(self._on_qt_move)
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(*HM_BG_DARK_BOT)
        self.renderer.SetBackground2(*HM_BG_DARK_TOP)
        self.renderer.GradientBackgroundOn()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self._anno = vtk.vtkCornerAnnotation()
        self._anno.SetLinearFontScaleFactor(2)
        self._anno.SetNonlinearFontScaleFactor(1)
        self._anno.SetMaximumFontSize(13)
        self._anno.SetText(vtk.vtkCornerAnnotation.UpperRight, "Model Info:")
        self._anno.GetTextProperty().SetColor(1.0, 1.0, 1.0)
        self._anno.GetTextProperty().SetFontFamilyToArial()
        self.renderer.AddViewProp(self._anno)
        self._setup_scale_bar()
        hl.addWidget(self.vtk_widget, 1)
        vl.addWidget(view_row, 1)
        vl.addWidget(self._build_gfx_toolbar())

        mid = QSplitter(Qt.Vertical)
        mid.addWidget(view_host)
        self.panel_bar = HmPanelBar()
        self.panel_bar.pageChanged.connect(self._on_page_changed)
        self.panel_bar.panelClicked.connect(self._on_panel_clicked)
        mid.addWidget(self.panel_bar)
        mid.setStretchFactor(0, 1)
        mid.setStretchFactor(1, 0)
        mid.setSizes([720, 168])

        hsplit = QSplitter(Qt.Horizontal)
        hsplit.addWidget(self._build_tab_area())
        hsplit.addWidget(mid)
        hsplit.setStretchFactor(0, 0)
        hsplit.setStretchFactor(1, 1)
        hsplit.setSizes([280, 1280])
        self.setCentralWidget(hsplit)

    def _icon_action(self, kind, tip, slot, checkable=False):
        a = QAction(HmIcons.get(kind), tip, self)
        a.setToolTip(tip)
        if checkable:
            a.setCheckable(True)
        a.triggered.connect(slot)
        return a

    def _build_view_strip(self):
        """视口左侧竖条: 对齐 HM 建模窗口边缘的选择/剖切图标."""
        strip = QToolBar()
        strip.setObjectName("ViewStrip")
        strip.setOrientation(Qt.Vertical)
        strip.setMovable(False)
        strip.setIconSize(QtCore.QSize(18, 18))
        strip.setFixedWidth(28)
        for kind, tip, slot in (
            ("pick", "Pick", lambda: self.target_combo.setCurrentText("元素")),
            ("ent_node", "Nodes", lambda: self.target_combo.setCurrentText("节点")),
            ("rotate", "Rotate center", lambda: self.interact_combo.setCurrentText("旋转")),
            ("box", "Window select", lambda: self.interact_combo.setCurrentText("框选")),
            ("section", "Section cut", lambda: self._nyi("section cut")),
            ("measure", "Distance", self._measure_distance),
            ("iso", "Isometric", lambda: self.view_along((1, 1, 1), (0, 0, 1))),
            ("fit", "Fit", self.fit_view),
        ):
            strip.addAction(self._icon_action(kind, tip, slot))
        return strip

    def _build_gfx_toolbar(self):
        """视口与面板之间的选择/着色子工具条 (By Comp, 实体过滤器)."""
        bar = QWidget()
        bar.setObjectName("GfxBar")
        bar.setFixedHeight(28)
        row = QHBoxLayout(bar)
        row.setContentsMargins(6, 2, 6, 2)
        row.setSpacing(4)
        row.addWidget(QLabel("Auto"))
        self.sel_filter_combo = QComboBox()
        self.sel_filter_combo.addItems(["Auto", "elems", "nodes", "surfs", "lines", "solids"])
        self.sel_filter_combo.setFixedWidth(72)
        self.sel_filter_combo.currentTextChanged.connect(self._on_sel_filter)
        row.addWidget(self.sel_filter_combo)
        for kind, tip, text in (
            ("ent_node", "nodes", "节点"),
            ("ent_line", "lines", None),
            ("ent_surf", "surfaces", None),
            ("ent_solid", "solids", None),
            ("ent_elem", "elems", "元素"),
        ):
            btn = QToolButton()
            btn.setIcon(HmIcons.get(kind, 16))
            btn.setToolTip(tip)
            btn.setAutoRaise(True)
            if text:
                btn.clicked.connect(lambda _=False, t=text: self.target_combo.setCurrentText(t))
            else:
                btn.clicked.connect(lambda _=False, n=tip: self._nyi(f"select {n}"))
            row.addWidget(btn)
        row.addWidget(QFrame())
        row.addWidget(QLabel("Color"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(["By Comp", "By Config", "By Elem Type", "Single"])
        self.color_combo.setFixedWidth(96)
        self.color_combo.currentTextChanged.connect(self._on_color_mode)
        row.addWidget(self.color_combo)
        for kind, tip, slot in (
            ("shaded", "Shaded + edges", lambda: self.set_display_mode(1)),
            ("wire", "Wireframe", lambda: self.set_display_mode(2)),
            ("hidden", "Hidden line", lambda: self.set_display_mode(0)),
            ("points", "Points", lambda: self.set_display_mode(3)),
            ("ent_node", "Toggle nodes", self._toolbar_toggle_nodes),
        ):
            btn = QToolButton()
            btn.setIcon(HmIcons.get(kind, 16))
            btn.setToolTip(tip)
            btn.setAutoRaise(True)
            btn.clicked.connect(slot)
            row.addWidget(btn)
        row.addStretch(1)
        return bar

    def _on_sel_filter(self, text):
        if text == "nodes":
            self.target_combo.setCurrentText("节点")
        elif text in ("Auto", "elems"):
            self.target_combo.setCurrentText("元素")

    def _on_color_mode(self, text):
        self._color_mode = text
        self.log(f"Color mode: {text}")
        if self.model is not None:
            self._rebuild_scene(fit=False)

    def _toolbar_toggle_nodes(self):
        self.act_show_nodes.setChecked(not self.act_show_nodes.isChecked())
        self._toggle_nodes()

    def _setup_scale_bar(self):
        """视口右下比例尺, 对齐 HM 2019 的 100L 标尺."""
        self._scale_actor = None
        try:
            sc = vtk.vtkLegendScaleActor()
            if hasattr(sc, "AllAxesOff"):
                sc.AllAxesOff()
            for name, on in (("SetTopAxisVisibility", 0),
                             ("SetLeftAxisVisibility", 0),
                             ("SetRightAxisVisibility", 0),
                             ("SetBottomAxisVisibility", 1)):
                if hasattr(sc, name):
                    getattr(sc, name)(on)
            if hasattr(sc, "LegendVisibilityOn"):
                sc.LegendVisibilityOn()
            for getter in ("GetLegendTitleProperty", "GetLegendLabelProperty"):
                if hasattr(sc, getter):
                    prop = getattr(sc, getter)()
                    prop.SetColor(1, 1, 1)
                    prop.SetFontFamilyToArial()
            if hasattr(sc, "GetBottomAxis"):
                try:
                    sc.GetBottomAxis().GetProperty().SetColor(1, 1, 1)
                except Exception:
                    pass
            self.renderer.AddViewProp(sc)
            self._scale_actor = sc
        except Exception:
            self._scale_actor = None

    def _build_tab_area(self):
        """左侧 Tab Area: Utility / Mask / Model / Materials + Entity Editor.

        官方: 'The tab area organizes browsers, Utility menus ... and other
        functionality not shown in the panel area.'
        """
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        self.left_tabs = tabs

        # Utility
        util = QWidget()
        uv = QVBoxLayout(util)
        uv.setContentsMargins(4, 4, 4, 4)
        uv.setSpacing(4)
        find_row = QHBoxLayout()
        self.find_edit = QLineEdit()
        self.find_edit.setPlaceholderText("Search tools / panels…")
        self.find_edit.returnPressed.connect(self._find_tool)
        find_btn = QPushButton("Find")
        find_btn.clicked.connect(self._find_tool)
        find_row.addWidget(self.find_edit, 1)
        find_row.addWidget(find_btn)
        uv.addLayout(find_row)
        uv.addWidget(QLabel("Message Log"))
        self.log_edit = QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setMaximumBlockCount(2000)
        uv.addWidget(self.log_edit, 1)
        tabs.addTab(util, "Utility")

        # Mask
        mask = QWidget()
        mv = QVBoxLayout(mask)
        mv.setContentsMargins(6, 6, 6, 6)
        mv.setSpacing(4)
        for text, slot in (
            ("Isolate selected", self._mask_isolate),
            ("Hide selected", self._mask_hide),
            ("Show all", self._mask_show_all),
            ("Reverse display", self._mask_reverse),
        ):
            b = QPushButton(text)
            b.setObjectName("HmPanelBtn")
            b.clicked.connect(slot)
            mv.addWidget(b)
        mv.addStretch(1)
        tabs.addTab(mask, "Mask")

        # Model browser
        model_tab = QWidget()
        ml = QVBoxLayout(model_tab)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(0)
        brow = QToolBar()
        brow.setIconSize(QtCore.QSize(16, 16))
        brow.setMovable(False)
        for kind, tip, slot in (
            ("refresh", "Refresh", self._rebuild_tree),
            ("find", "Find", self._find_in_tree),
            ("filter", "Filter empty folders", self._toggle_empty_folders),
            ("create", "Create collector", self._tree_create_selected),
            ("del", "Delete", self._tree_delete_selected),
        ):
            brow.addAction(self._icon_action(kind, tip, slot))
        ml.addWidget(brow)
        self.tree = QTreeWidget()
        self.tree.setObjectName("HmModelTree")
        self.tree.setHeaderLabels(["Entities", "ID", "Include"])
        self.tree.setColumnCount(3)
        self.tree.setRootIsDecorated(True)
        self.tree.setUniformRowHeights(True)
        self.tree.setAlternatingRowColors(True)
        self.tree.setAnimated(True)
        self.tree.setIconSize(QtCore.QSize(16, 16))
        self.tree.setColumnWidth(0, 168)
        self.tree.setColumnWidth(1, 42)
        self.tree.setColumnWidth(2, 52)
        self.tree.itemChanged.connect(self._on_tree_item_changed)
        self.tree.itemSelectionChanged.connect(self._on_tree_selected)
        self.tree.itemDoubleClicked.connect(self._on_tree_double_clicked)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._on_tree_menu)
        ml.addWidget(self.tree, 1)
        tabs.addTab(model_tab, "Model")

        # Materials library
        tabs.addTab(self._build_material_library(), "Materials")
        tabs.setCurrentIndex(2)

        wrap = QWidget()
        wrap.setObjectName("PaneFrame")
        wv = QVBoxLayout(wrap)
        wv.setContentsMargins(0, 0, 0, 0)
        wv.setSpacing(0)
        tbar = QLabel("Tab Area")
        tbar.setObjectName("PaneTitleBar")
        wv.addWidget(tbar)
        wv.addWidget(tabs, 3)

        # Entity Editor (Name Value)
        ee_title = QLabel("Name Value")
        ee_title.setObjectName("PaneTitleBar")
        wv.addWidget(ee_title)
        self.info = QTextBrowser()
        self.info.setMinimumHeight(140)
        wv.addWidget(self.info, 2)
        self.editor_table = QTableWidget(0, 2)
        self.editor_table.setHorizontalHeaderLabels(["Name", "Value"])
        self.editor_table.horizontalHeader().setStretchLastSection(True)
        self.editor_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.editor_table.verticalHeader().setVisible(False)
        self.editor_table.setMinimumHeight(90)
        wv.addWidget(self.editor_table, 1)
        wrap.setMinimumWidth(260)
        wrap.setMaximumWidth(440)
        return wrap

    def _build_material_library(self):
        """材料库: 预置卡片 + 模型内已解码 collectors."""
        page = QWidget()
        vl = QVBoxLayout(page)
        vl.setContentsMargins(4, 4, 4, 4)
        vl.setSpacing(4)
        head = QHBoxLayout()
        head.addWidget(QLabel("Material Library"))
        self.mat_search = QLineEdit()
        self.mat_search.setPlaceholderText("Filter…")
        self.mat_search.textChanged.connect(self._filter_mat_table)
        head.addWidget(self.mat_search, 1)
        vl.addLayout(head)
        self.mat_table = QTableWidget(0, 5)
        self.mat_table.setHorizontalHeaderLabels(
            ["Name", "Type", "Density", "E", "Nu"])
        self.mat_table.horizontalHeader().setStretchLastSection(True)
        self.mat_table.verticalHeader().setVisible(False)
        self.mat_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.mat_table.setIconSize(QtCore.QSize(16, 16))
        self.mat_table.itemSelectionChanged.connect(self._on_mat_selected)
        vl.addWidget(self.mat_table, 1)
        row = QHBoxLayout()
        assign = QPushButton("Assign to Component")
        assign.setObjectName("HmPanelBtn")
        assign.clicked.connect(self._assign_material)
        row.addWidget(assign)
        row.addStretch(1)
        vl.addLayout(row)
        self._refresh_mat_table()
        return page

    def _refresh_mat_table(self):
        rows = []
        if self.model is not None:
            for mid, nm in sorted(self.model.mats.items()):
                rows.append((nm, "collector", mid, "", "", True))
        for name, typ, dens, e, nu in HM_MAT_LIBRARY:
            rows.append((name, typ, dens, e, nu, False))
        self.mat_table.setRowCount(len(rows))
        icon = HmIcons.get("leaf_mat", 16)
        for i, rec in enumerate(rows):
            name, typ = rec[0], rec[1]
            it = QTableWidgetItem(name)
            it.setIcon(icon)
            it.setData(Qt.UserRole, rec)
            self.mat_table.setItem(i, 0, it)
            self.mat_table.setItem(i, 1, QTableWidgetItem(str(typ)))
            if rec[-1]:
                self.mat_table.setItem(i, 2, QTableWidgetItem(str(rec[2])))
                self.mat_table.setItem(i, 3, QTableWidgetItem(""))
                self.mat_table.setItem(i, 4, QTableWidgetItem(""))
            else:
                self.mat_table.setItem(i, 2, QTableWidgetItem(f"{rec[2]:.3g}"))
                self.mat_table.setItem(i, 3, QTableWidgetItem(f"{rec[3]:.4g}"))
                self.mat_table.setItem(i, 4, QTableWidgetItem(f"{rec[4]:.2f}"))

    def _filter_mat_table(self, text):
        q = (text or "").strip().lower()
        for i in range(self.mat_table.rowCount()):
            it = self.mat_table.item(i, 0)
            hide = bool(q) and q not in (it.text() if it else "").lower()
            self.mat_table.setRowHidden(i, hide)

    def _on_mat_selected(self):
        items = self.mat_table.selectedItems()
        if not items:
            return
        rec = items[0].data(Qt.UserRole)
        if not rec:
            return
        if rec[-1]:
            self._fill_editor([
                ("Name", rec[0]), ("Type", "Material collector"),
                ("ID", rec[2]),
            ])
        else:
            self._fill_editor([
                ("Name", rec[0]), ("Card", rec[1]),
                ("Density", rec[2]), ("E", rec[3]), ("Nu", rec[4]),
            ])

    def _assign_material(self):
        items = self.mat_table.selectedItems()
        if not items:
            self.log("Material Library: select a material first")
            return
        name = items[0].text()
        self.log(f"Material Library: assign '{name}' "
                 "(card write-back not available in this decoder)")
        self.statusBar().showMessage(f"Assigned {name} (preview only)")

    def _show_material_library(self):
        if hasattr(self, "left_tabs"):
            for i in range(self.left_tabs.count()):
                if self.left_tabs.tabText(i) == "Materials":
                    self.left_tabs.setCurrentIndex(i)
                    break

    def _find_in_tree(self):
        q, ok = QInputDialog.getText(self, "Find", "Entity name / ID:")
        if not ok or not (q or "").strip():
            return
        q = q.strip().lower()

        def walk(item):
            if q in item.text(0).lower() or q == item.text(1).lower():
                self.tree.setCurrentItem(item)
                self.tree.scrollToItem(item)
                return True
            for i in range(item.childCount()):
                if walk(item.child(i)):
                    return True
            return False

        for i in range(self.tree.topLevelItemCount()):
            if walk(self.tree.topLevelItem(i)):
                return
        self.log(f"Find: no match for '{q}'")

    def _toggle_empty_folders(self):
        for i in range(self.tree.topLevelItemCount()):
            it = self.tree.topLevelItem(i)
            kind, val = it.data(0, Qt.UserRole) or (None, None)
            if kind == "folder" and it.childCount() == 0:
                it.setHidden(not it.isHidden())

    def _tree_create_selected(self):
        item = self.tree.currentItem()
        kind, val = (item.data(0, Qt.UserRole) if item else (None, None)) or (None, None)
        self._create_collector(kind or "folder", val or "Components")

    def _tree_delete_selected(self):
        self.log("Delete collector: binary .hm write-back is not supported")

    def _build_menus(self):
        # 菜单顺序对齐 HyperMesh 2019 截图 / menubar_overview_r.htm
        mb = self.menuBar()
        m_file = mb.addMenu("&File")
        self._add_action(m_file, "Open .hm…", self.open_hm_dialog, "Ctrl+O")
        self._add_action(m_file, "Open Tutorial Model…", self.open_tutorial_dialog)
        self._add_action(m_file, "Open Project (.hmj)…", self.open_hmj_dialog)
        m_file.addSeparator()
        self.act_save = self._add_action(m_file, "Save Project (.hmj)", self.save_hmj, "Ctrl+S")
        self.act_save_as = self._add_action(m_file, "Save Project As…",
                                           lambda: self.save_hmj(True))
        m_file.addSeparator()
        m_exp = m_file.addMenu("Export")
        self.act_inp = self._add_action(m_exp, "Abaqus INP…", self.export_inp)
        self.act_step = self._add_action(m_exp, "STEP (AP203)…", self.export_step)
        self.act_iges = self._add_action(m_exp, "IGES (points/lines)…", self.export_iges)
        self.act_csv = self._add_action(m_exp, "CSV (nodes+elems)…", self.export_csv)
        m_file.addSeparator()
        self._add_action(m_file, "Exit", self.close, "Ctrl+Q")

        m_edit = mb.addMenu("&Edit")
        self.act_undo = self._add_action(m_edit, "Undo", self.undo, "Ctrl+Z")
        self.act_redo = self._add_action(m_edit, "Redo", self.redo, "Ctrl+Y")
        m_edit.addSeparator()
        self.act_move = self._add_action(m_edit, "Translate Nodes…",
                                        self.move_node_dialog, "M")
        self.act_add_node = self._add_action(m_edit, "Create Node…",
                                            self.add_node_dialog)
        self.act_add_elem = self._add_action(m_edit, "Create Element…",
                                            self.add_element_dialog)
        self.act_flip = self._add_action(m_edit, "Reverse 2D Normals",
                                        self.flip_selected)
        self.act_ren_node = self._add_action(m_edit, "Renumber Nodes…",
                                            self.renumber_node_dialog)
        self.act_ren_elem = self._add_action(m_edit, "Renumber Elements…",
                                            self.renumber_element_dialog)
        m_edit.addSeparator()
        self.act_del = self._add_action(m_edit, "Delete Selected",
                                       self.delete_selected, "Delete")
        m_edit.addSeparator()
        self.act_sel_id = self._add_action(m_edit, "Select by ID…",
                                          self.select_by_id_dialog, "Ctrl+I")
        self.act_sel_all = self._add_action(m_edit, "Select All",
                                           self.select_all, "Ctrl+A")
        self.act_sel_inv = self._add_action(m_edit, "Reverse Selection",
                                           self.invert_selection)
        self.act_sel_none = self._add_action(m_edit, "Clear Selection",
                                            self.clear_selection, "Esc")

        m_view = mb.addMenu("&View")
        m_mode = m_view.addMenu("Visualization")
        self._mode_actions = []
        for i, name in enumerate(DISPLAY_MODES):
            a = QAction(name, self)
            a.setCheckable(True)
            a.setChecked(i == self._display_mode)
            a.triggered.connect(lambda _c=False, k=i: self.set_display_mode(k))
            m_mode.addAction(a)
            self._mode_actions.append(a)
        m_view.addSeparator()
        self.act_show_nodes = QAction("Nodes", self)
        self.act_show_nodes.setCheckable(True)
        self.act_show_nodes.triggered.connect(self._toggle_nodes)
        m_view.addAction(self.act_show_nodes)
        self.act_show_disp = QAction("Display Points", self)
        self.act_show_disp.setCheckable(True)
        self.act_show_disp.setChecked(True)
        self.act_show_disp.triggered.connect(self._toggle_disp)
        m_view.addAction(self.act_show_disp)
        self.act_show_geo = QAction("Geometry Points", self)
        self.act_show_geo.setCheckable(True)
        self.act_show_geo.setChecked(True)
        self.act_show_geo.triggered.connect(self._toggle_geo)
        m_view.addAction(self.act_show_geo)
        self.act_axes = QAction("Orientation Marker", self)
        self.act_axes.setCheckable(True)
        self.act_axes.setChecked(True)
        self.act_axes.triggered.connect(self._toggle_axes)
        m_view.addAction(self.act_axes)
        m_view.addSeparator()
        self._add_action(m_view, "Fit", self.fit_view, "F")
        m_std = m_view.addMenu("Standard Views")
        for label, d, up in (("Front (+Y)", (0, 1, 0), (0, 0, 1)),
                             ("Back (-Y)", (0, -1, 0), (0, 0, 1)),
                             ("Left (-X)", (-1, 0, 0), (0, 0, 1)),
                             ("Right (+X)", (1, 0, 0), (0, 0, 1)),
                             ("Top (-Z)", (0, 0, -1), (0, 1, 0)),
                             ("Bottom (+Z)", (0, 0, 1), (0, 1, 0)),
                             ("Isometric", (1, 1, 1), (0, 0, 1))):
            self._add_action(m_std, label,
                             lambda _c=False, dd=d, uu=up: self.view_along(dd, uu))
        m_view.addSeparator()
        self._add_action(m_view, "Toggle Background (Light/Dark)",
                        self.toggle_background)

        def _page_menu(title, page):
            m = mb.addMenu(title)
            for col in HM_PANEL_PAGES.get(page, []):
                for name in col:
                    self._add_action(m, name,
                                     lambda _c=False, pg=page, pn=name:
                                     self._on_panel_clicked(pg, pn))
            return m

        _page_menu("&Collectors", "Analysis")
        _page_menu("&Geometry", "Geom")
        _page_menu("&Mesh", "2D")
        m_conn = mb.addMenu("Co&nnectors")
        for name in ("connectors", "spotweld", "welds"):
            self._add_action(m_conn, name,
                             lambda _c=False, pn=name: self._on_panel_clicked("1D", pn))
        m_mat = mb.addMenu("&Materials")
        self._add_action(m_mat, "Material Library…", self._show_material_library)
        self._add_action(m_mat, "Materials collector",
                         lambda: self._focus_tree_folder("Materials"))
        mb.addMenu("&Properties").addAction(
            self._nyi_action("Properties collector"))
        _page_menu("&BCs", "Analysis")
        m_setup = mb.addMenu("&Setup")
        self._add_action(m_setup, "User Profile…", self._show_user_profile)
        self._add_action(m_setup, "Control Cards",
                         lambda: self._on_panel_clicked("Analysis", "control cards"))
        _page_menu("&Tools", "Tool")
        mb.addMenu("M&orphing").addAction(self._nyi_action("Morphing"))
        _page_menu("&Post", "Post")
        mb.addMenu("&XYPlots").addAction(self._nyi_action("XY Plots"))
        m_pref = mb.addMenu("Pr&eferences")
        self._add_action(m_pref, "Light Modeling Background",
                         lambda: self._set_background(False))
        self._add_action(m_pref, "Dark Modeling Background",
                         lambda: self._set_background(True))
        m_app = mb.addMenu("&Applications")
        self._add_action(m_app, "Open hmopengl.exe…", self._launch_hmopengl)

        m_help = mb.addMenu("&Help")
        self._add_action(m_help, "HyperMesh User Interface", self.open_hm_ui_help)
        self._add_action(m_help, "HyperMesh Help Manual", self.open_hm_help)
        self._add_action(m_help, "Tutorials", self.open_hm_tutorials)
        self._add_action(m_help, "Panels Reference", self.open_hm_panels)
        self._add_action(m_help, "Tcl / Command Reference (HWD)", self.open_hwd_help)
        m_help.addSeparator()
        self._add_action(m_help, "About", self.about_dialog)

    def _nyi_action(self, name):
        a = QAction(name, self)
        a.triggered.connect(lambda: self._nyi(name))
        return a

    def _build_toolbar(self):
        tb = self.addToolBar("Standard")
        tb.setObjectName("main_toolbar")
        tb.setMovable(False)
        tb.setIconSize(QtCore.QSize(20, 20))
        for kind, tip, slot in (
            ("new", "New", lambda: self._nyi("File / New")),
            ("open", "Open .hm", self.open_hm_dialog),
            ("save", "Save project", self.save_hmj),
            ("print", "Print / snapshot", self._snapshot_view),
        ):
            tb.addAction(self._icon_action(kind, tip, slot))
        tb.addSeparator()
        for kind, tip, slot in (
            ("undo", "Undo", self.undo),
            ("redo", "Redo", self.redo),
            ("find", "Find", self._find_in_tree),
            ("mask", "Mask", self._mask_hide),
            ("isolate", "Isolate", self._mask_isolate),
            ("numbers", "Numbers", self.select_by_id_dialog),
            ("count", "Count", self._count_selection),
            ("help", "Help", self.open_hm_ui_help),
        ):
            tb.addAction(self._icon_action(kind, tip, slot))

        tb2 = self.addToolBar("Visualization")
        tb2.setMovable(False)
        tb2.setIconSize(QtCore.QSize(20, 20))
        for kind, tip, slot in (
            ("fit", "Fit", self.fit_view),
            ("front", "Front", lambda: self.view_along((0, 1, 0), (0, 0, 1))),
            ("top", "Top", lambda: self.view_along((0, 0, -1), (0, 1, 0))),
            ("side", "Right", lambda: self.view_along((1, 0, 0), (0, 0, 1))),
            ("iso", "Isometric", lambda: self.view_along((1, 1, 1), (0, 0, 1))),
            ("pan", "Pan (middle mouse)", lambda: self.log("Pan: hold middle mouse")),
            ("zoom", "Zoom (wheel)", lambda: self.log("Zoom: mouse wheel")),
            ("rotate", "Rotate (trackball)",
             lambda: self.interact_combo.setCurrentText("旋转")),
            ("box", "Window select",
             lambda: self.interact_combo.setCurrentText("框选")),
            ("shaded", "Shaded + edges", lambda: self.set_display_mode(1)),
            ("wire", "Wireframe", lambda: self.set_display_mode(2)),
            ("hidden", "Shaded", lambda: self.set_display_mode(0)),
            ("del", "Delete", self.delete_selected),
        ):
            tb2.addAction(self._icon_action(kind, tip, slot))
        tb2.addSeparator()
        tb2.addWidget(QLabel("  Display: "))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(DISPLAY_MODES)
        self.mode_combo.setCurrentIndex(self._display_mode)
        self.mode_combo.currentIndexChanged.connect(self.set_display_mode)
        tb2.addWidget(self.mode_combo)
        tb2.addWidget(QLabel("  Select: "))
        self.target_combo = QComboBox()
        self.target_combo.addItems(["元素", "节点"])
        self.target_combo.currentTextChanged.connect(self._set_pick_target)
        tb2.addWidget(self.target_combo)
        tb2.addWidget(QLabel("  Interact: "))
        self.interact_combo = QComboBox()
        self.interact_combo.addItems(["旋转", "框选"])
        self.interact_combo.currentTextChanged.connect(self._set_interact_mode)
        tb2.addWidget(self.interact_combo)

    def _build_statusbar(self):
        self.statusBar().showMessage("Ready")
        self.page_label = QLabel("Geometry")
        self.comp_swatch = QLabel()
        self.comp_swatch.setFixedSize(12, 12)
        self.comp_name = QLabel("")
        self.coord_label = QLabel("")
        self.count_label = QLabel("")
        self.model_label = QLabel("Model")
        self.statusBar().addPermanentWidget(self.page_label)
        self.statusBar().addPermanentWidget(self.comp_swatch)
        self.statusBar().addPermanentWidget(self.comp_name)
        self.statusBar().addPermanentWidget(self.coord_label, 1)
        self.statusBar().addPermanentWidget(self.count_label)
        self.statusBar().addPermanentWidget(self.model_label)

    def _add_action(self, menu, text, slot, shortcut=None):
        a = QAction(text, self)
        if shortcut:
            a.setShortcut(QtGui.QKeySequence(shortcut))
            a.setShortcutContext(Qt.WindowShortcut)
        a.triggered.connect(slot)
        menu.addAction(a)
        return a

    # ---------------- VTK 初始化 (延迟到窗口可见, 参考 cab_gui) ----------------
    def showEvent(self, event):  # noqa: N802
        super().showEvent(event)
        if self._startup_redraw:
            QTimer.singleShot(0, self._finish_startup)

    def _finish_startup(self):
        if not self._iren_ready:
            self._ensure_interactor()
        self._startup_redraw = False
        self._render()
        QTimer.singleShot(100, self._render)

    def _ensure_interactor(self):
        if self._iren_ready:
            return
        iren = self.vtk_widget.GetRenderWindow().GetInteractor()
        style = vtk.vtkInteractorStyleTrackballCamera()
        try:
            style.AutoAdjustCameraClippingRangeOff()
        except Exception:
            pass
        self._trackball_style = style
        iren.SetInteractorStyle(style)
        # 鼠标 press/release/move 走 Qt 层信号 (见 HmView  docstring);
        # 交互器层面只保留相机裁剪范围复位等辅助观察者.
        iren.AddObserver("EndInteractionEvent", self._on_end_interaction, 1.0)
        iren.AddObserver("MouseWheelForwardEvent", self._on_end_interaction, 1.0)
        iren.AddObserver("MouseWheelBackwardEvent", self._on_end_interaction, 1.0)
        self._cell_picker = vtk.vtkCellPicker()
        self._cell_picker.SetTolerance(0.004)
        self._area_picker = vtk.vtkAreaPicker()
        iren.SetPicker(self._area_picker)
        self._rubber_style = vtk.vtkInteractorStyleRubberBandPick()
        # 注意: EndPickEvent 由 vtkRenderWindowInteractor::EndPickCallback
        # 在"交互器"上触发 (不是样式上), 观察者必须挂在 iren 上.
        iren.AddObserver("EndPickEvent", self._on_rubber_end, 1.0)
        try:
            self.vtk_widget.Initialize()
        except Exception:
            iren.Initialize()
        self._iren_ready = True
        self._toggle_axes(self.act_axes.isChecked())

    def _render(self):
        try:
            self.vtk_widget.GetRenderWindow().Render()
        except Exception:
            pass

    def _on_end_interaction(self, *_a):
        try:
            self.renderer.ResetCameraClippingRange()
        except Exception:
            pass

    # ---------------- 文件打开/保存 ----------------
    def open_hm_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "打开 HyperMesh 模型", "",
            "HyperMesh 模型 (*.hm *.hm10);;所有文件 (*)")
        if path:
            self.open_path(path)

    def open_tutorial_dialog(self):
        start = str(ALTAIR_ROOT / "tutorials" / "hm")
        if not Path(start).is_dir():
            start = ""
        path, _ = QFileDialog.getOpenFileName(
            self, "打开教程模型", start,
            "HyperMesh 模型 (*.hm *.hm10);;所有文件 (*)")
        if path:
            self.open_path(path)

    def open_hmj_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "打开编辑工程", "", "HM 编辑工程 (*.hmj);;所有文件 (*)")
        if path:
            self.open_path(path)

    def open_path(self, path):
        path = str(path)
        ext = Path(path).suffix.lower()
        if ext == ".hmj":
            self._open_hmj(path)
        else:
            self._open_hm(path)

    def _open_hm(self, path):
        if self.loader is not None and self.loader.isRunning():
            QMessageBox.information(self, APP_TITLE, "正在加载中, 请稍候…")
            return
        self.log(f"开始解码: {path}")
        self._progress = QProgressDialog("正在解码 .hm 模型…", None, 0, 0, self)
        self._progress.setWindowTitle(APP_TITLE)
        self._progress.setWindowModality(Qt.WindowModal)
        self._progress.setMinimumDuration(0)
        self._progress.show()
        self.loader = LoaderThread(path, self)
        self.loader.loaded.connect(lambda m, p=path: self._on_loaded(p, m))
        self.loader.failed.connect(self._on_load_failed)
        self.loader.start()

    def _on_loaded(self, path, model):
        self._progress.close()
        self.model = EditableModel(model, source_path=path)
        self.model.hmj_path = None
        secs = getattr(model, "_load_seconds", 0.0)
        self.log(f"解码完成 ({secs:.1f}s): 节点 {len(self.model.nodes)}, "
                 f"单元 {len(self.model.elements)}, "
                 f"显示点 {len(self.model.display_points)}, "
                 f"几何点 {len(self.model.geo_points)}, "
                 f"DB v{self.model.db_version}, 变体 {self.model.element_variant}")
        self._refresh_title(path)
        self.sel_elems.clear()
        self.sel_nodes.clear()
        self._set_model_info(path)
        self._rebuild_scene(fit=True)
        self._refresh_mat_table()
        self._update_status_comp()
        self._update_edit_actions()

    def _on_load_failed(self, err):
        self._progress.close()
        self.log("解码失败:\n" + err)
        QMessageBox.critical(self, APP_TITLE,
                             "解码失败 (详见消息日志):\n" + err.splitlines()[-1])

    def _open_hmj(self, path):
        try:
            self.model = EditableModel.from_json(path)
            self.model.hmj_path = path
        except Exception as exc:
            QMessageBox.critical(self, APP_TITLE, f"工程打开失败:\n{exc}")
            return
        self.log(f"工程已打开: {path} (节点 {len(self.model.nodes)}, "
                 f"单元 {len(self.model.elements)})")
        self._refresh_title(path)
        self.sel_elems.clear()
        self.sel_nodes.clear()
        self._set_model_info(path)
        self._rebuild_scene(fit=True)
        self._refresh_mat_table()
        self._update_status_comp()
        self._update_edit_actions()

    def save_hmj(self, save_as=False):
        if self.model is None:
            return
        path = getattr(self.model, "hmj_path", None)
        if save_as or not path:
            path, _ = QFileDialog.getSaveFileName(
                self, "保存编辑工程", "", "HM 编辑工程 (*.hmj)")
            if not path:
                return
            if not path.lower().endswith(".hmj"):
                path += ".hmj"
        try:
            self.model.save_json(path)
            self.model.hmj_path = path
            self.log(f"工程已保存: {path}")
            self.statusBar().showMessage(f"已保存 {path}", 5000)
        except Exception as exc:
            QMessageBox.critical(self, APP_TITLE, f"保存失败:\n{exc}")

    # ---------------- 导出 ----------------
    def export_inp(self):
        if not self._need_model():
            return
        path, _ = QFileDialog.getSaveFileName(self, "导出 INP", "", "Abaqus INP (*.inp)")
        if not path:
            return
        try:
            from hmdecoder.export import export_inp
            QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
            export_inp(self.model.to_hmmodel(), path)
            self.log(f"INP 已导出: {path}")
        except Exception as exc:
            QMessageBox.critical(self, APP_TITLE, f"导出失败:\n{exc}")
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def export_step(self):
        if not self._need_model():
            return
        path, _ = QFileDialog.getSaveFileName(self, "导出 STEP", "", "STEP (*.step *.stp)")
        if not path:
            return
        try:
            from hmdecoder.export_step import export_step
            QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
            export_step(self.model.to_hmmodel(), path)
            self.log(f"STEP 已导出: {path}")
        except Exception as exc:
            QMessageBox.critical(self, APP_TITLE, f"导出失败:\n{exc}")
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def export_iges(self):
        if not self._need_model():
            return
        path, _ = QFileDialog.getSaveFileName(self, "导出 IGES", "", "IGES (*.iges *.igs)")
        if not path:
            return
        try:
            from hmdecoder.export_iges import export_iges
            QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
            export_iges(self.model.to_hmmodel(), path)
            self.log(f"IGES 已导出: {path}")
        except Exception as exc:
            QMessageBox.critical(self, APP_TITLE, f"导出失败:\n{exc}")
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

    def export_csv(self):
        if not self._need_model():
            return
        d = QFileDialog.getExistingDirectory(self, "选择 CSV 输出目录")
        if not d:
            return
        try:
            np_path = Path(d) / "nodes.csv"
            ep_path = Path(d) / "elements.csv"
            with open(np_path, "w", encoding="utf-8") as f:
                f.write("id,x,y,z\n")
                for nid in sorted(self.model.nodes):
                    n = self.model.nodes[nid]
                    f.write(f"{n.id},{n.x:.10g},{n.y:.10g},{n.z:.10g}\n")
            with open(ep_path, "w", encoding="utf-8") as f:
                f.write("id,config,nnodes,nodes\n")
                for e in self.model.elements:
                    f.write(f"{e.id},{e.config},{len(e.nodes)},"
                            f"\"{' '.join(str(v) for v in e.nodes)}\"\n")
            self.log(f"CSV 已导出: {np_path}, {ep_path}")
        except Exception as exc:
            QMessageBox.critical(self, APP_TITLE, f"导出失败:\n{exc}")

    def _need_model(self):
        if self.model is None:
            QMessageBox.information(self, APP_TITLE, "请先打开模型")
            return False
        return True

    # ---------------- 场景构建 ----------------
    def _rebuild_scene(self, fit=False):
        self._ensure_interactor()
        t0 = time.time()
        # 清空旧 actor
        for g in self._groups.values():
            self.renderer.RemoveActor(g.actor)
        self._groups.clear()
        for a in (self._node_actor, self._disp_actor, self._geo_actor,
                  self._elem_hl_actor, self._node_hl_actor,
                  getattr(self, "_geo_hl_actor", None)):
            if a is not None:
                self.renderer.RemoveActor(a)
        self._node_actor = self._disp_actor = self._geo_actor = None
        self._elem_hl_actor = self._node_hl_actor = self._geo_hl_actor = None
        self.sel_elems.clear()
        self.sel_nodes.clear()
        self.sel_geo_points.clear()

        if self.model is None:
            self._rebuild_tree()
            self._update_counts()
            self._render()
            return

        # 共享点集
        nids = sorted(self.model.nodes)
        self._idx2nid = nids
        self._nid2idx = {n: i for i, n in enumerate(nids)}
        xyz = np.array([[self.model.nodes[n].x, self.model.nodes[n].y,
                         self.model.nodes[n].z] for n in nids],
                       dtype=float).reshape(-1, 3)
        self._vpts = vtk.vtkPoints()
        self._vpts.SetData(numpy_to_vtk(xyz if xyz.size else np.zeros((0, 3)),
                                        deep=True))

        # 单元分组: 有 comps 按组件分组 (M3.3 comp 勾选显隐), 否则按 config
        by_group = {}
        for i, e in enumerate(self.model.elements):
            by_group.setdefault(self._group_key(e), []).append((i, e))
        total_skipped = 0
        size_order = sorted(by_group, key=lambda k: -len(by_group[k]))
        color_of = {k: PALETTE[i % len(PALETTE)] for i, k in enumerate(size_order)}
        for key in sorted(by_group, key=lambda k: (k[0], k[1])):
            grid, skipped = build_group_grid(self._vpts, self._nid2idx, by_group[key])
            total_skipped += skipped
            _old, visible = self._group_style.get(key, (None, True))
            base = color_of.get(key, PALETTE[0])
            mode = getattr(self, "_color_mode", "By Comp")
            if mode == "Single":
                color = PALETTE[0]
            elif mode in ("By Config", "By Elem Type") and key[0] == "comp":
                cfgs = [e.config for _i, e in by_group[key]]
                color = (PALETTE[Counter(cfgs).most_common(1)[0][0] % len(PALETTE)]
                         if cfgs else base)
            else:
                color = base
            self._group_style[key] = (color, visible)
            g = GroupView(key, grid, color)
            g.visible = visible
            g.actor.SetVisibility(visible)
            self._apply_display_mode(g.actor)
            self.renderer.AddActor(g.actor)
            self._groups[key] = g
        if total_skipped:
            self.log(f"警告: {total_skipped} 个单元引用了缺失节点, 已跳过显示")

        # 节点云
        self._node_poly = build_node_cloud(self._vpts, nids)
        nm = vtk.vtkPolyDataMapper()
        nm.SetInputData(self._node_poly)
        nm.ScalarVisibilityOff()
        self._node_actor = vtk.vtkActor()
        self._node_actor.SetMapper(nm)
        self._node_actor.GetProperty().SetColor(0.95, 0.95, 0.60)
        self._node_actor.GetProperty().SetPointSize(4)
        try:
            self._node_actor.GetProperty().SetRenderPointsAsSpheres(True)
        except Exception:
            pass
        show_nodes = self.act_show_nodes.isChecked()
        if len(nids) > 200_000 and show_nodes:
            self.act_show_nodes.setChecked(False)
            show_nodes = False
            self.log("节点数 > 20 万, 节点云默认关闭 (视图菜单可开启)")
        self._node_actor.SetVisibility(show_nodes)
        self.renderer.AddActor(self._node_actor)

        # 显示点 / 几何点
        self._disp_actor = self._make_points_actor(
            self.model.display_points, (1.0, 0.30, 0.30), 7,
            self.act_show_disp.isChecked())
        self._geo_actor = self._make_points_actor(
            self.model.geo_points, (0.30, 0.55, 1.0), 7,
            self.act_show_geo.isChecked())

        self._rebuild_tree()
        self._update_counts()
        self._update_info()
        if fit:
            self.fit_view()
            QTimer.singleShot(200, self.fit_view)
        else:
            self._render()
        self.log(f"场景重建完成 ({time.time() - t0:.1f}s), "
                 f"分组 {len(self._groups)} 个")

    def _make_points_actor(self, points, color, size, visible):
        if not points:
            return None
        pd, _ids = build_points_poly(points)
        m = vtk.vtkPolyDataMapper()
        m.SetInputData(pd)
        m.ScalarVisibilityOff()
        a = vtk.vtkActor()
        a.SetMapper(m)
        a.GetProperty().SetColor(*color)
        a.GetProperty().SetPointSize(size)
        try:
            a.GetProperty().SetRenderPointsAsSpheres(True)
        except Exception:
            pass
        a.SetVisibility(visible)
        a.PickableOff()
        self.renderer.AddActor(a)
        return a

    def _apply_display_mode(self, actor):
        prop = actor.GetProperty()
        prop.SetEdgeVisibility(0)
        if self._display_mode == 0:
            prop.SetRepresentationToSurface()
        elif self._display_mode == 1:
            prop.SetRepresentationToSurface()
            prop.SetEdgeVisibility(1)
        elif self._display_mode == 2:
            prop.SetRepresentationToWireframe()
        else:
            prop.SetRepresentationToPoints()

    def set_display_mode(self, k):
        self._display_mode = k
        for i, a in enumerate(self._mode_actions):
            a.setChecked(i == k)
        if self.mode_combo.currentIndex() != k:
            self.mode_combo.setCurrentIndex(k)
        for g in self._groups.values():
            self._apply_display_mode(g.actor)
        self._render()

    # ---------------- 模型树 ----------------
    def _group_key(self, elem):
        """元素的可视分组键: 有 comp collector 数据按组件, 否则按 config (M3.3)."""
        if self.model.comps:
            return ("comp", elem.comp or 0)
        return ("cfg", elem.config)

    def _collector_folders(self):
        """官方 Model Browser 类别文件夹数据: [(label, leaf_kind, {id: name}), ...].

        非 comp 类别从 model.mats/props/groups/others 分流; Sets/Load/Assemblies
        按名称模式识别 (与 M_/P_ 同类启发式, 已按 HM oracle 校准: truck sets=
        Set_*/SLAVE_* 579/587, loadcols=Airbag* 2/2, assemblies=assem*; type 516
        XtraNodes/RigidWallPlan 为 sets 族残影 (37/44 在 HM 已不存在), 留 Others
        不进 Sets 以免幽灵计数), 未匹配项进 Others 且名称不丢.
        """
        asm, sets, loads = [], [], []
        rest = []
        for cid, nm in self.model.others:
            if nm.startswith("assem"):
                asm.append((cid, nm))
            elif nm.startswith(("Set_", "SLAVE_", "C_S^_")):
                sets.append((cid, nm))
            elif nm.startswith("Airbag"):
                loads.append((cid, nm))
            else:
                rest.append((cid, nm))
        return [
            ("Assemblies", "asm", asm),
            ("Components", "comp", None),          # 全量列, 单独处理
            ("Materials", "mat", self.model.mats),
            ("Properties", "prop", self.model.props),
            ("Sets", "set", sets),
            ("Groups", "grp", self.model.groups),
            ("Load", "load", loads),
            ("System", "sys", {}),
            ("Vector", "vec", {}),
            ("Others", "other", rest),
        ]

    def _mk_tree_item(self, text, kind, val, icon=None, eid="", include=""):
        it = QTreeWidgetItem([text, str(eid) if eid != "" else "", include])
        it.setData(0, Qt.UserRole, (kind, val))
        if icon is not None:
            it.setIcon(0, icon)
        return it

    def _rebuild_tree(self):
        """Model Browser: Entities / ID / Include 三列, 按层级配图标.

        M3.3: comps 全量列出 (含无元素组件, id 含跳号), 勾选控制该组件元素显隐
        (渲染按 comp 分组); 其余类别按名称启发式分流, 未匹配进 Others.
        无 comp 数据 (v12+ 等) 回落到按 config 分组的旧树.
        """
        self.tree.blockSignals(True)
        self.tree.clear()
        if self.model is not None:
            if self.model.comps:
                cg = self.model.comp_groups()
                for label, kind, data in self._collector_folders():
                    n = (len(self.model.comps) if label == "Components"
                         else len(data))
                    it = self._mk_tree_item(
                        f"{label} ({n})", "folder", label,
                        HmIcons.get(FOLDER_ICONS.get(label, "folder_other"), 16))
                    if label == "Components":
                        for cid in sorted(self.model.comps):
                            nm = self.model.comps[cid]
                            cnt = cg.get(cid, 0)
                            key = ("comp", cid)
                            color, visible = self._group_style.get(
                                key, (PALETTE[cid % len(PALETTE)] if cid
                                      else (0.60, 0.60, 0.60), True))
                            child = self._mk_tree_item(
                                f"{nm} ({cnt})", "comp", cid,
                                HmIcons.swatch(color or (0.6, 0.6, 0.6)),
                                eid=cid, include="0")
                            child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                            child.setCheckState(
                                0, Qt.Checked if visible else Qt.Unchecked)
                            it.addChild(child)
                    else:
                        items = (sorted(data.items()) if isinstance(data, dict)
                                 else sorted(data))
                        leaf_icon = HmIcons.get(LEAF_ICONS.get(kind, "folder_other"), 16)
                        for cid, nm in items:
                            it.addChild(self._mk_tree_item(
                                nm, kind, cid, leaf_icon, eid=cid, include="0"))
                    self.tree.addTopLevelItem(it)
                    it.setExpanded(label == "Components" and len(self.model.comps) <= 64)
            else:
                counts = self.model.config_groups()
                it_comp = self._mk_tree_item(
                    f"Components ({len(counts)})", "comps", None,
                    HmIcons.get("folder_comp", 16))
                for cfg in sorted(counts):
                    name, _nn, cat = config_info(cfg)
                    color = self._group_style.get(("cfg", cfg), (None, None))[0]
                    if color is None:
                        color = PALETTE[cfg % len(PALETTE)]
                    child = self._mk_tree_item(
                        f"{name} [{cat}] ({counts[cfg]})", "group", cfg,
                        HmIcons.swatch(color), eid=cfg, include="0")
                    child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                    visible = self._group_style.get(("cfg", cfg), (None, True))[1]
                    child.setCheckState(0, Qt.Checked if visible else Qt.Unchecked)
                    it_comp.addChild(child)
                self.tree.addTopLevelItem(it_comp)
                it_comp.setExpanded(True)

            it_title = self._mk_tree_item(
                "Titles (1)", "folder", "Titles", HmIcons.get("folder_title", 16))
            it_title.addChild(self._mk_tree_item(
                "Model", "title", 1, HmIcons.get("leaf_title", 16), eid=1, include="0"))
            self.tree.addTopLevelItem(it_title)

            it_nodes = self._mk_tree_item(
                f"Nodes ({len(self.model.nodes)})", "nodes", None,
                HmIcons.get("folder_nodes", 16))
            it_nodes.setFlags(it_nodes.flags() | Qt.ItemIsUserCheckable)
            it_nodes.setCheckState(0, Qt.Checked if self.act_show_nodes.isChecked()
                                   else Qt.Unchecked)
            self.tree.addTopLevelItem(it_nodes)
            self.tree.addTopLevelItem(self._mk_tree_item(
                f"Elements ({len(self.model.elements)})", "elems", None,
                HmIcons.get("folder_elems", 16)))
            it_geo = self._mk_tree_item(
                "Geometry", "geofolder", None, HmIcons.get("folder_geo", 16))
            if self.model.display_points:
                it = self._mk_tree_item(
                    f"Display Points ({len(self.model.display_points)})",
                    "disp", None, HmIcons.get("leaf_disp", 16))
                it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
                it.setCheckState(0, Qt.Checked if self.act_show_disp.isChecked()
                                 else Qt.Unchecked)
                it_geo.addChild(it)
            if self.model.geo_points:
                it = self._mk_tree_item(
                    f"Geometry Points ({len(self.model.geo_points)})",
                    "geo", None, HmIcons.get("leaf_geo", 16))
                it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
                it.setCheckState(0, Qt.Checked if self.act_show_geo.isChecked()
                                 else Qt.Unchecked)
                it_geo.addChild(it)
            self.tree.addTopLevelItem(it_geo)
            it_geo.setExpanded(True)
        self.tree.blockSignals(False)
        self._update_status_comp()

    def _on_tree_item_changed(self, item, _col):
        kind, val = item.data(0, Qt.UserRole) or (None, None)
        on = item.checkState(0) == Qt.Checked
        if kind == "group":
            key = ("cfg", val)
            g = self._groups.get(key)
            if g is not None:
                g.visible = on
                g.actor.SetVisibility(on)
                color, _ = self._group_style.get(key, (None, True))
                self._group_style[key] = (color, on)
                self._render()
        elif kind == "comp":
            # M3.3: 组件勾选控制该组件元素显隐 (渲染按 comp 分组)
            key = ("comp", val)
            g = self._groups.get(key)
            if g is not None:
                g.visible = on
                g.actor.SetVisibility(on)
            color, _ = self._group_style.get(key, (None, True))
            self._group_style[key] = (color, on)
            self._render()
        elif kind == "nodes":
            self.act_show_nodes.setChecked(on)
            self._toggle_nodes()
        elif kind == "disp":
            self.act_show_disp.setChecked(on)
            self._toggle_disp()
        elif kind == "geo":
            self.act_show_geo.setChecked(on)
            self._toggle_geo()

    def _on_tree_selected(self):
        items = self.tree.selectedItems()
        if not items or self.model is None:
            return
        kind, val = items[0].data(0, Qt.UserRole) or (None, None)
        if kind == "info":
            b = self.model.bounds()
            bb = (f"BBox: X[{b[0]:.6g}, {b[1]:.6g}] "
                  f"Y[{b[2]:.6g}, {b[3]:.6g}] Z[{b[4]:.6g}, {b[5]:.6g}]") if b else "empty"
            text = (
                f"Source: {self.model.source_path or '(project)'}\n"
                f"DB version: {self.model.db_version}\n"
                f"Element variant: {self.model.element_variant}\n"
                f"Nodes: {len(self.model.nodes)}\n"
                f"Elements: {len(self.model.elements)}\n"
                f"Display points: {len(self.model.display_points)}\n"
                f"Geometry points: {len(self.model.geo_points)}\n{bb}\n\n"
                f"Config distribution:\n" + "\n".join(
                    f"  {cfg} {config_info(cfg)[0]}: {cnt}"
                    for cfg, cnt in sorted(self.model.config_groups().items())))
            self.info.setPlainText(text)
            self._fill_editor([
                ("Name", Path(self.model.source_path or "").name or "(project)"),
                ("Nodes", len(self.model.nodes)),
                ("Elements", len(self.model.elements)),
                ("DB", self.model.db_version),
                ("Variant", self.model.element_variant),
            ])
        elif kind == "group":
            counts = self.model.config_groups()
            name, nn, cat = config_info(val)
            self.info.setPlainText(
                f"Component  config {val}  {name}\nCategory: {cat}\n"
                f"Standard nodes: {nn or 'variable'}\nCount: {counts.get(val, 0)}\n"
                f"(double-click to select all elements in this component)")
            self._fill_editor([
                ("config", val), ("type", name), ("category", cat),
                ("count", counts.get(val, 0)), ("nodes/elem", nn or "var"),
            ])
        elif kind == "comp":
            nm = self.model.comps.get(val, "")
            cnt = self.model.comp_groups().get(val, 0)
            self.info.setPlainText(
                f"Component {val}  {nm}\nElements: {cnt}\n"
                f"(double-click to select all elements, checkbox to show/hide)")
            self._fill_editor([
                ("ID", val), ("Type", "Component"),
                ("Name", nm), ("Elements", cnt), ("Include", 0),
            ])
            self._update_status_comp(val)
        elif kind == "title":
            self.info.setPlainText("Title collector: Model")
            self._fill_editor([("ID", val), ("Type", "Title"), ("Name", "Model")])
        elif kind == "folder":
            self.info.setPlainText(f"Model Browser / {val}\n"
                                   f"(右键 Create/Edit/Card)")
        elif kind in ("asm", "mat", "prop", "set", "grp", "load", "sys",
                      "vec", "other"):
            store = {"asm": "Assemblies", "mat": "Materials", "prop": "Properties",
                     "set": "Sets", "grp": "Groups", "load": "Load",
                     "sys": "System", "vec": "Vector", "other": "Others"}
            nm = None
            for d in (self.model.mats, self.model.props, self.model.groups):
                if val in d:
                    nm = d[val]
                    break
            if nm is None:
                for oid, onm in self.model.others:
                    if oid == val:
                        nm = onm
                        break
            self.info.setPlainText(
                f"{store.get(kind, kind)} collector {val}\nName: {nm or ''}")
            self._fill_editor([("ID", val), ("Type", store.get(kind, kind)),
                               ("Name", nm or "")])

    def _on_tree_double_clicked(self, item, _col):
        kind, val = item.data(0, Qt.UserRole) or (None, None)
        if kind == "group" and self.model is not None:
            idxs = {i for i, e in enumerate(self.model.elements) if e.config == val}
            self._set_elem_selection(idxs, 0)
            self.log(f"已选择 config {val} 分组全部 {len(idxs)} 个单元")
        elif kind == "comp" and self.model is not None:
            idxs = {i for i, e in enumerate(self.model.elements) if e.comp == val}
            self._set_elem_selection(idxs, 0)
            self.log(f"已选择组件 {val} 全部 {len(idxs)} 个单元")

    # ---------------- 右键菜单 (Create / Edit / Card) ----------------
    def _on_tree_menu(self, pos):
        item = self.tree.itemAt(pos)
        if item is None or self.model is None:
            return
        menu = QMenu(self)
        act_create = menu.addAction("Create…")
        act_edit = menu.addAction("Edit…")
        menu.addSeparator()
        act_card = menu.addAction("Card…")
        act = menu.exec_(self.tree.viewport().mapToGlobal(pos))
        if act is None:
            return
        kind, val = item.data(0, Qt.UserRole) or (None, None)
        if act is act_create:
            self._create_collector(kind, val)
        elif act is act_edit:
            self._edit_collector(kind, val, item.text(0))
        elif act is act_card:
            QMessageBox.information(
                self, "Card Editor",
                "卡片数据引用已定位但语义未解码 (M6.1 计划).\n"
                "MAT/PROP 记录尾部 float 卡数据的语义映射待 hwtemplex.dll 模板对照.")

    def _create_collector(self, kind, val):
        if kind != "folder":
            self.log("Create: 请选中文件夹项")
            return
        if val in ("System", "Vector", "Others"):
            self.log(f"Create: {val} 记录类型解码未覆盖, 暂不支持创建")
            return
        name, ok = QInputDialog.getText(self, f"Create {val}", "Name:")
        if not ok or not name.strip():
            return
        name = name.strip()
        if val == "Components":
            cid = max(self.model.comps, default=0) + 1
            self.model.comps[cid] = name
            self._group_style[("comp", cid)] = (None, True)
            self.log(f"创建组件 {cid} {name} (内存, 无写回)")
        elif val == "Materials":
            cid = max(self.model.mats, default=0) + 1
            self.model.mats[cid] = name
            self.log(f"创建材料 {cid} {name} (内存)")
        elif val == "Properties":
            cid = max(self.model.props, default=0) + 1
            self.model.props[cid] = name
            self.log(f"创建属性 {cid} {name} (内存)")
        elif val == "Groups":
            cid = max(self.model.groups, default=0) + 1
            self.model.groups[cid] = name
            self.log(f"创建组 {cid} {name} (内存)")
        else:
            # Sets/Load/Assemblies 为 others 的视图分流; 命名提示前缀规则
            prefix = {"Assemblies": "assem_", "Sets": "Set_",
                      "Load": "Airbag"}.get(val, "")
            if prefix and not name.startswith(prefix.split("_")[0]):
                self.log(f"{val} 名称未含 {prefix}* 前缀, 将落入 Others 文件夹")
            cid = max((oid for oid, _ in self.model.others), default=0) + 1
            self.model.others.append((cid, name))
            self.log(f"创建 {val} 收集器 {cid} {name} (内存)")
        self._rebuild_tree()
        self._update_info()

    def _edit_collector(self, kind, val, old_label):
        store = {"comp": self.model.comps, "mat": self.model.mats,
                 "prop": self.model.props, "grp": self.model.groups}
        d = store.get(kind)
        if d is not None and val in d:
            old = d[val]
        else:
            idx = next((i for i, (oid, _n) in enumerate(self.model.others)
                        if oid == val), None)
            if idx is None:
                self.log("Edit: 该实体暂不支持 (节点/元素/几何编辑在其它面板)")
                return
            old = self.model.others[idx][1]
        new, ok = QInputDialog.getText(
            self, "Edit Collectors", "Name:", text=old)
        if ok and new.strip() and new.strip() != old:
            if d is not None and val in d:
                d[val] = new.strip()
            else:
                idx = next(i for i, (oid, _n) in enumerate(self.model.others)
                           if oid == val and _n == old)
                self.model.others[idx] = (val, new.strip())
            self._rebuild_tree()
            self._update_info()
            self.log(f"重命名 collector {val}: {old} -> {new.strip()} (内存)")

    # ---------------- 图层开关 ----------------
    def _toggle_nodes(self, *_a):
        if self._node_actor is not None:
            self._node_actor.SetVisibility(self.act_show_nodes.isChecked())
            self._render()
        self._sync_tree_checks()

    def _toggle_disp(self, *_a):
        if self._disp_actor is not None:
            self._disp_actor.SetVisibility(self.act_show_disp.isChecked())
            self._render()
        self._sync_tree_checks()

    def _toggle_geo(self, *_a):
        if self._geo_actor is not None:
            self._geo_actor.SetVisibility(self.act_show_geo.isChecked())
            self._render()
        self._sync_tree_checks()

    def _sync_tree_checks(self):
        self.tree.blockSignals(True)

        def walk(item):
            kind, _v = item.data(0, Qt.UserRole) or (None, None)
            if kind == "nodes":
                item.setCheckState(0, Qt.Checked if self.act_show_nodes.isChecked()
                                   else Qt.Unchecked)
            elif kind == "disp":
                item.setCheckState(0, Qt.Checked if self.act_show_disp.isChecked()
                                   else Qt.Unchecked)
            elif kind == "geo":
                item.setCheckState(0, Qt.Checked if self.act_show_geo.isChecked()
                                   else Qt.Unchecked)
            for i in range(item.childCount()):
                walk(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            walk(self.tree.topLevelItem(i))
        self.tree.blockSignals(False)

    def _toggle_axes(self, on):
        if not self._iren_ready:
            return
        if self._orientation is not None:
            self._orientation.SetEnabled(0)
            self._orientation = None
        if on:
            axes = vtk.vtkAxesActor()
            om = vtk.vtkOrientationMarkerWidget()
            om.SetOrientationMarker(axes)
            om.SetInteractor(self.vtk_widget.GetRenderWindow().GetInteractor())
            om.SetViewport(0.0, 0.0, 0.16, 0.16)
            om.SetEnabled(1)
            om.InteractiveOff()
            self._orientation = om
        self._render()

    # ---------------- 视图 ----------------
    def fit_view(self):
        try:
            self.renderer.ResetCamera()
            self.renderer.ResetCameraClippingRange()
        except Exception:
            pass
        self._render()

    def view_along(self, direction, up):
        if self.model is None:
            return
        b = self.model.bounds()
        if not b:
            return
        cx, cy, cz = (b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2
        diag = max(1e-6, ((b[1] - b[0]) ** 2 + (b[3] - b[2]) ** 2
                          + (b[5] - b[4]) ** 2) ** 0.5)
        d = np.asarray(direction, dtype=float)
        d = d / np.linalg.norm(d)
        cam = self.renderer.GetActiveCamera()
        cam.SetFocalPoint(cx, cy, cz)
        cam.SetPosition(cx + d[0] * diag * 1.6, cy + d[1] * diag * 1.6,
                        cz + d[2] * diag * 1.6)
        cam.SetViewUp(*up)
        self.renderer.ResetCameraClippingRange()
        self._render()

    def toggle_background(self):
        self._set_background(not self._bg_dark)

    def _set_background(self, dark):
        self._bg_dark = bool(dark)
        if self._bg_dark:
            self.renderer.SetBackground(*HM_BG_DARK_BOT)
            self.renderer.SetBackground2(*HM_BG_DARK_TOP)
            fg = (1.0, 1.0, 1.0)
        else:
            self.renderer.SetBackground(*HM_BG_LIGHT_BOT)
            self.renderer.SetBackground2(*HM_BG_LIGHT_TOP)
            fg = (0.08, 0.08, 0.10)
        if self._anno:
            self._anno.GetTextProperty().SetColor(*fg)
        if self._scale_actor is not None:
            for getter in ("GetLegendTitleProperty", "GetLegendLabelProperty"):
                if hasattr(self._scale_actor, getter):
                    getattr(self._scale_actor, getter)().SetColor(*fg)
        self._render()

    def _set_model_info(self, path):
        text = f"Model Info: {path}" if path else "Model Info:"
        if self._anno is not None:
            self._anno.SetText(vtk.vtkCornerAnnotation.UpperRight, text)

    def _refresh_title(self, path=None):
        if path:
            name = Path(path).name
        elif self.model is not None and getattr(self.model, "source_path", None):
            name = Path(self.model.source_path).name
        else:
            name = "HyperMesh"
        self.setWindowTitle(f"{name} - HyperMesh 2019 - {self._user_profile}")

    def _update_status_comp(self, cid=None):
        if self.model is None or not getattr(self.model, "comps", None):
            self.comp_swatch.clear()
            self.comp_name.setText("")
            return
        if cid is None:
            items = self.tree.selectedItems() if hasattr(self, "tree") else []
            if items:
                kind, val = items[0].data(0, Qt.UserRole) or (None, None)
                if kind == "comp":
                    cid = val
            if cid is None:
                cid = next(iter(sorted(self.model.comps)), None)
        if cid is None:
            return
        name = self.model.comps.get(cid, "")
        color, _vis = self._group_style.get(
            ("comp", cid), (PALETTE[cid % len(PALETTE)], True))
        pm = QPixmap(12, 12)
        pm.fill(QColor.fromRgbF(*(color or (0.6, 0.6, 0.6))))
        self.comp_swatch.setPixmap(pm)
        self.comp_name.setText(name)

    def _focus_tree_folder(self, label):
        if hasattr(self, "left_tabs"):
            self.left_tabs.setCurrentIndex(2)
        for i in range(self.tree.topLevelItemCount()):
            it = self.tree.topLevelItem(i)
            kind, val = it.data(0, Qt.UserRole) or (None, None)
            if kind == "folder" and val == label:
                self.tree.setCurrentItem(it)
                it.setExpanded(True)
                return

    def _snapshot_view(self):
        if not hasattr(self, "vtk_widget"):
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save snapshot", "view.png", "PNG (*.png)")
        if not path:
            return
        w2i = vtk.vtkWindowToImageFilter()
        w2i.SetInput(self.vtk_widget.GetRenderWindow())
        w2i.ReadFrontBufferOff()
        w2i.Update()
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(path)
        writer.SetInputConnection(w2i.GetOutputPort())
        writer.Write()
        self.log(f"Snapshot: {path}")

    # ---------------- 拾取与选择 ----------------
    def _set_pick_target(self, text):
        self._pick_target = text

    def _set_interact_mode(self, text):
        self._interact = text
        if not self._iren_ready:
            return
        iren = self.vtk_widget.GetRenderWindow().GetInteractor()
        if text == "框选":
            iren.SetInteractorStyle(self._rubber_style)
            # RubberBandPick 默认处于 ORIENT 模式 (左键=旋转),
            # 必须 StartSelect() 才会进入拖框选择模式.
            self._rubber_style.StartSelect()
            self.log("框选模式: 左键拖框选择 (Ctrl 追加); 切回 '旋转' 恢复视角操作")
        else:
            iren.SetInteractorStyle(self._trackball_style)

    def _iren_pos(self):
        """当前鼠标位置 (VTK 显示坐标, y 已翻转), 与 picker 坐标系一致."""
        iren = self.vtk_widget.GetRenderWindow().GetInteractor()
        return iren.GetEventPosition()

    def _on_qt_move(self):
        try:
            x, y = self._iren_pos()
            picker = vtk.vtkWorldPointPicker()
            picker.Pick(float(x), float(y), 0.0, self.renderer)
            wx, wy, wz = picker.GetPickPosition()
            self.coord_label.setText(f"({wx:.6g}, {wy:.6g}, {wz:.6g})")
        except Exception:
            pass

    def _on_qt_press(self):
        self._press_pos = self._iren_pos()

    def _on_qt_release(self):
        if self._press_pos is None:
            return
        x, y = self._iren_pos()
        dragged = abs(x - self._press_pos[0]) + abs(y - self._press_pos[1]) > 6
        add = bool(QApplication.keyboardModifiers() & Qt.ControlModifier)
        if self._interact == "框选":
            if dragged:
                self._area_pick(self._press_pos[0], self._press_pos[1], x, y, add)
            return
        if self._interact != "旋转" or dragged:
            return
        self._pick_at(x, y, add=add)

    def _area_pick(self, x0, y0, x1, y1, add=False):
        """Qt 层框选: 不依赖 RubberBandPick 的 EndPickEvent (焦点会吞掉 release)."""
        xmin, xmax = sorted((float(x0), float(x1)))
        ymin, ymax = sorted((float(y0), float(y1)))
        try:
            self._area_picker.AreaPick(xmin, ymin, xmax, ymax, self.renderer)
        except Exception:
            return
        self._apply_frustum(add)

    def _pick_at(self, x, y, add=False):
        if self.model is None:
            return
        picker = self._cell_picker
        # 按拾取目标限制候选 actor: 节点模式只拾取节点云 (否则被
        # 遮挡在外面的单元表面截获), 元素模式只拾取单元分组.
        picker.InitializePickList()
        if self._pick_target == "节点":
            if self._node_actor is None or not self._node_actor.GetVisibility():
                return
            picker.AddPickList(self._node_actor)
            picker.SetTolerance(0.02)   # 顶点小, 放宽容差
        else:
            for g in self._groups.values():
                if g.visible and g.actor is not None:
                    picker.AddPickList(g.actor)
            picker.SetTolerance(0.004)
        picker.PickFromListOn()
        picker.Pick(float(x), float(y), 0.0, self.renderer)
        picker.PickFromListOff()
        actor = picker.GetActor()
        cell = picker.GetCellId()
        if actor is None or cell < 0:
            if not add:
                self.clear_selection()
            return
        if actor is self._node_actor:
            arr = self._node_poly.GetCellData().GetArray("nid")
            if arr and cell < arr.GetNumberOfTuples():
                nid = int(arr.GetValue(cell))
                self._set_node_selection({nid}, 1 if add else 0)
            return
        for g in self._groups.values():
            if actor is g.actor:
                arr = g.grid.GetCellData().GetArray("elem_idx")
                if arr and cell < arr.GetNumberOfTuples():
                    eidx = int(arr.GetValue(cell))
                    self._set_elem_selection({eidx}, 1 if add else 0)
                return

    def _on_rubber_end(self, *_a):
        add = bool(QApplication.keyboardModifiers() & Qt.ControlModifier)
        self._apply_frustum(add)

    def _apply_frustum(self, add=False):
        if self.model is None:
            return
        frustum = self._area_picker.GetFrustum()
        if frustum is None:
            return
        mode = 1 if add else 0
        if self._pick_target == "节点":
            nids = self._frustum_ids(self._node_poly, frustum, "nid")
            self._set_node_selection(nids, mode)
            self.log(f"框选节点 {len(nids)} 个")
        else:
            idxs = set()
            for g in self._groups.values():
                if not g.visible:
                    continue
                idxs |= self._frustum_ids(g.grid, frustum, "elem_idx")
            self._set_elem_selection(idxs, mode)
            self.log(f"框选单元 {len(idxs)} 个")

    @staticmethod
    def _frustum_ids(dataset, frustum, array_name):
        """视锥提取: 返回 dataset 中落入 frustum 的单元的 array_name 数据值集合."""
        out = set()
        if dataset is None or frustum is None or dataset.GetNumberOfCells() == 0:
            return out
        try:
            ext = vtk.vtkExtractSelectedFrustum()
            ext.SetInputData(dataset)
            ext.SetFrustum(frustum)
            ext.Update()
            sel = ext.GetOutput()
            ids = sel.GetCellData().GetArray("vtkOriginalCellIds")
            src = dataset.GetCellData().GetArray(array_name)
            if ids is None or src is None:
                return out
            n_src = src.GetNumberOfTuples()
            for i in range(ids.GetNumberOfTuples()):
                oc = int(ids.GetValue(i))
                if 0 <= oc < n_src:
                    out.add(int(src.GetValue(oc)))
        except Exception:
            pass
        return out

    # ---------------- 选择状态 ----------------
    def _set_elem_selection(self, idxs, mode):
        if mode == 0:
            self.sel_elems = set(idxs)
        elif mode == 1:
            self.sel_elems |= set(idxs)
        else:
            self.sel_elems -= set(idxs)
        self.sel_nodes.clear()
        self._rebuild_highlights()
        self._update_info()
        self._update_counts()

    def _set_node_selection(self, nids, mode):
        if mode == 0:
            self.sel_nodes = set(nids)
        elif mode == 1:
            self.sel_nodes |= set(nids)
        else:
            self.sel_nodes -= set(nids)
        self.sel_elems.clear()
        self._rebuild_highlights()
        self._update_info()
        self._update_counts()

    def clear_selection(self):
        self.sel_elems.clear()
        self.sel_nodes.clear()
        self._rebuild_highlights()
        self._update_info()
        self._update_counts()

    def select_all(self):
        if self.model is None:
            return
        if self._pick_target == "节点":
            self._set_node_selection(set(self.model.nodes), 0)
        else:
            self._set_elem_selection(set(range(len(self.model.elements))), 0)

    def invert_selection(self):
        if self.model is None:
            return
        if self._pick_target == "节点":
            self._set_node_selection(set(self.model.nodes) - self.sel_nodes, 0)
        else:
            self._set_elem_selection(
                set(range(len(self.model.elements))) - self.sel_elems, 0)

    def select_by_id_dialog(self):
        if not self._need_model():
            return
        dlg = SelectByIdDialog(self, self._pick_target)
        if dlg.exec_() != QDialog.Accepted:
            return
        ids, mode = dlg.values()
        if self._pick_target == "节点":
            self._set_node_selection(ids & set(self.model.nodes), mode)
            self.log(f"按 ID 选择节点: 命中 {len(ids & set(self.model.nodes))} 个")
        else:
            want = ids
            idxs = {i for i, e in enumerate(self.model.elements) if e.id in want}
            self._set_elem_selection(idxs, mode)
            self.log(f"按 ID 选择单元: 命中 {len(idxs)} 个")

    def select_geo_point_dialog(self):
        """Geom / point edit 面板: 按 id 选几何点, 高亮 + 写 Entity Editor.

        几何点 (M4.1 db 11.05 规整段) 与显示点不同: 是 BREP 拓扑中的 vertex,
        HyperMesh 2019 官方面板 *createpoint / *createpoints 的对象.
        高亮复用 _geo_actor 的可见性, 选中集以 overlay actor 渲染.
        """
        if not self._need_model():
            return
        n = len(self.model.geo_points)
        if n == 0:
            QMessageBox.information(self, APP_TITLE,
                "本模型未解码几何点 (db 11.05 规整段为空或本格式未实现).\n"
                "见 docs/NYI_INVENTORY.md §M4.1.")
            return
        from PyQt5.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Geom / point edit",
            f"输入几何点 id (1..{max(self.model.geo_points)}, 共 {n} 个),\n"
            "支持范围/逗号分隔 (例: 1,3,5-12):",
            text="1")
        if not ok or not text.strip():
            return
        ids = _parse_id_list(text)
        hit = sorted(i for i in ids if i in self.model.geo_points)
        miss = sorted(i for i in ids if i not in self.model.geo_points)
        if not hit:
            QMessageBox.warning(self, APP_TITLE,
                f"命中 0 (遗漏 {len(miss)}); 输入范围或 id 越界.")
            self.statusBar().showMessage(f"Geom point edit: 命中 0")
            return
        # 持久化选集: 让后续 Geom / length 面板可直接消费
        self.sel_geo_points = set(hit)
        # Entity Editor 摘要: 按选中 id 升序列坐标
        lines = [f"Geom points selected: {len(hit)}"]
        for i in hit[:200]:
            gp = self.model.geo_points[i]
            lines.append(f"  id={i:>6}  x={gp.x: .6f}  y={gp.y: .6f}  z={gp.z: .6f}")
        if len(hit) > 200:
            lines.append(f"  ... 共 {len(hit)} 个, 仅显示前 200")
        self.info.setPlainText("\n".join(lines))
        # 高亮: 在几何点 actor 上叠加, 或新建一个 overlay actor
        self._highlight_geo_points(hit)
        self.log(f"Geom point edit: 命中 {len(hit)} 个, 遗漏 {len(miss)}")
        self.statusBar().showMessage(f"Geom point edit: 命中 {len(hit)}")

    def _highlight_geo_points(self, ids):
        if getattr(self, "_geo_hl_actor", None) is not None:
            self.renderer.RemoveActor(self._geo_hl_actor)
            self._geo_hl_actor = None
        if self._vpts is None or not ids or not self.model.geo_points:
            return
        # geo_points 用独立 actor (蓝色 7pt), 它直接持有 poly_data; 不能在同一
        # polydata 上叠加选集. 用同坐标点重建一个选中集 actor.
        pts = vtk.vtkPoints()
        for i in ids:
            gp = self.model.geo_points[i]
            pts.InsertNextPoint(gp.x, gp.y, gp.z)
        pd = vtk.vtkPolyData()
        pd.SetPoints(pts)
        pd.SetVerts(make_cell_array([[i] for i in range(len(ids))]))
        m = vtk.vtkPolyDataMapper()
        m.SetInputData(pd)
        m.ScalarVisibilityOff()
        a = vtk.vtkActor()
        a.SetMapper(m)
        a.GetProperty().SetColor(1.0, 0.85, 0.10)  # 高对比黄
        a.GetProperty().SetPointSize(11)
        try:
            a.GetProperty().SetRenderPointsAsSpheres(True)
        except Exception:
            pass
        a.PickableOff()
        self.renderer.AddActor(a)
        self._geo_hl_actor = a
        self._render()

    def _rebuild_highlights(self):
        for a in (self._elem_hl_actor, self._node_hl_actor):
            if a is not None:
                self.renderer.RemoveActor(a)
        self._elem_hl_actor = self._node_hl_actor = None
        if self.model is None or self._vpts is None:
            return
        if self.sel_elems:
            indexed = [(i, self.model.elements[i]) for i in sorted(self.sel_elems)
                       if 0 <= i < len(self.model.elements)]
            grid, _ = build_group_grid(self._vpts, self._nid2idx, indexed)
            sf = vtk.vtkDataSetSurfaceFilter()
            sf.SetInputData(grid)
            try:
                sf.SetNonlinearSubdivisionLevel(1)
            except Exception:
                pass
            m = vtk.vtkPolyDataMapper()
            m.SetInputConnection(sf.GetOutputPort())
            m.ScalarVisibilityOff()
            a = vtk.vtkActor()
            a.SetMapper(m)
            a.GetProperty().SetColor(1.0, 0.15, 0.15)
            a.GetProperty().SetEdgeColor(1.0, 1.0, 0.2)
            a.GetProperty().SetEdgeVisibility(1)
            a.GetProperty().SetLineWidth(3)
            a.GetProperty().SetPointSize(8)
            a.PickableOff()
            self.renderer.AddActor(a)
            self._elem_hl_actor = a
        if self.sel_nodes:
            idxs = [self._nid2idx[n] for n in sorted(self.sel_nodes)
                    if n in self._nid2idx]
            if idxs:
                pd = vtk.vtkPolyData()
                pd.SetPoints(self._vpts)
                pd.SetVerts(make_cell_array([[i] for i in idxs]))
                m = vtk.vtkPolyDataMapper()
                m.SetInputData(pd)
                m.ScalarVisibilityOff()
                a = vtk.vtkActor()
                a.SetMapper(m)
                a.GetProperty().SetColor(0.2, 0.5, 1.0)
                a.GetProperty().SetPointSize(9)
                try:
                    a.GetProperty().SetRenderPointsAsSpheres(True)
                except Exception:
                    pass
                a.PickableOff()
                self.renderer.AddActor(a)
                self._node_hl_actor = a
        self._render()

    # ---------------- 信息/状态 ----------------
    def _update_info(self):
        if self.model is None:
            self.info.setPlainText("No model loaded")
            self._fill_editor([])
            return
        lines = []
        if self.sel_elems:
            idxs = sorted(self.sel_elems)
            lines.append(f"选中单元: {len(idxs)} 个")
            for i in idxs[:30]:
                e = self.model.elements[i]
                name, _nn, cat = config_info(e.config)
                c = self.model.elem_centroid(e)
                cs = (f"质心 ({c[0]:.6g}, {c[1]:.6g}, {c[2]:.6g})"
                      if c else "质心 (缺失节点)")
                lines.append(
                    f"#{i}  eid={e.id}  {e.config} {name} [{cat}]\n"
                    f"    节点: {' '.join(str(v) for v in e.nodes)}\n    {cs}")
            if len(idxs) > 30:
                lines.append(f"… 其余 {len(idxs) - 30} 个从略")
        elif self.sel_nodes:
            nids = sorted(self.sel_nodes)
            lines.append(f"选中节点: {len(nids)} 个")
            for nid in nids[:30]:
                n = self.model.nodes.get(nid)
                if n is None:
                    continue
                ne = len(self.model.elements_of_nodes([nid]))
                lines.append(f"节点 {nid}: ({n.x:.8g}, {n.y:.8g}, {n.z:.8g})"
                             f"  关联单元 {ne}")
            if len(nids) > 30:
                lines.append(f"… 其余 {len(nids) - 30} 个从略")
        else:
            lines.append("No selection.\n\nLeft-click to pick (toolbar: 元素/节点);\n"
                         "Ctrl+click to add; Interact = 框选 for window pick;\n"
                         "Edit > Select by ID / Select All / Reverse.")
        self.info.setPlainText("\n".join(lines))
        rows = []
        if self.sel_elems:
            i = sorted(self.sel_elems)[0]
            e = self.model.elements[i]
            name, nn, cat = config_info(e.config)
            rows = [("entity", "element"), ("index", i), ("id", e.id),
                    ("config", e.config), ("type", name), ("category", cat),
                    ("nodes", " ".join(str(v) for v in e.nodes))]
        elif self.sel_nodes:
            nid = sorted(self.sel_nodes)[0]
            n = self.model.nodes.get(nid)
            if n is not None:
                rows = [("entity", "node"), ("id", nid),
                        ("x", n.x), ("y", n.y), ("z", n.z)]
        self._fill_editor(rows)

    def _update_counts(self):
        if self.model is None:
            self.count_label.setText("")
            return
        s = f"节点 {len(self.model.nodes)} | 单元 {len(self.model.elements)}"
        if self.sel_elems:
            s += f" | 选中单元 {len(self.sel_elems)}"
        if self.sel_nodes:
            s += f" | 选中节点 {len(self.sel_nodes)}"
        self.count_label.setText(s)

    def log(self, msg):
        self.log_edit.appendPlainText(
            f"[{time.strftime('%H:%M:%S')}] {msg}")

    # ---------------- 编辑操作 ----------------
    def _update_edit_actions(self):
        has = self.model is not None
        for a in (self.act_save, self.act_save_as, self.act_inp, self.act_step,
                  self.act_iges, self.act_csv, self.act_move, self.act_add_node,
                  self.act_add_elem, self.act_flip, self.act_ren_node,
                  self.act_ren_elem, self.act_del, self.act_sel_id,
                  self.act_sel_all, self.act_sel_inv, self.act_sel_none):
            a.setEnabled(has)
        self._refresh_undo_actions()

    def _refresh_undo_actions(self):
        has = self.model is not None
        self.act_undo.setEnabled(has and bool(self.model.undo_stack))
        self.act_redo.setEnabled(has and bool(self.model.redo_stack))
        if has:
            u = self.model.undo_stack[-1].label if self.model.undo_stack else ""
            r = self.model.redo_stack[-1].label if self.model.redo_stack else ""
            self.act_undo.setText(f"Undo {u}".rstrip())
            self.act_redo.setText(f"Redo {r}".rstrip())

    def undo(self):
        if self.model is None:
            return
        cmd = self.model.undo()
        if cmd is None:
            return
        self.log(f"撤销: {cmd.label}")
        self._after_edit(cmd)

    def redo(self):
        if self.model is None:
            return
        cmd = self.model.redo()
        if cmd is None:
            return
        self.log(f"重做: {cmd.label}")
        self._after_edit(cmd)

    def _after_edit(self, cmd):
        """编辑后刷新: 纯移动走点集快路径, 结构性修改全量重建."""
        self._refresh_undo_actions()
        if isinstance(cmd, CmdMoveNodes) and self._vpts is not None:
            for nid, _o, _n in cmd.moves:
                n = self.model.nodes.get(nid)
                idx = self._nid2idx.get(nid)
                if n is not None and idx is not None:
                    self._vpts.SetPoint(idx, n.x, n.y, n.z)
            self._vpts.Modified()
            self._rebuild_highlights()
            self._update_info()
            self._render()
        else:
            self._rebuild_scene(fit=False)

    def move_node_dialog(self):
        if not self._need_model():
            return
        nids = self.sel_nodes
        if not nids and len(self.sel_elems) == 1:
            # 便捷: 选中单个单元时移动其所有节点? 不 — 提示选择节点
            pass
        if not nids:
            nid, ok = QInputDialog.getInt(self, "移动节点", "节点 ID:",
                                          1, 1, 10_000_000)
            if not ok:
                return
            if nid not in self.model.nodes:
                QMessageBox.warning(self, APP_TITLE, f"节点 {nid} 不存在")
                return
            nids = {nid}
        dlg = MoveNodeDialog(self, self.model, nids)
        if dlg.exec_() != QDialog.Accepted:
            return
        cmd = dlg.command()
        if cmd is None:
            return
        self.model.apply(cmd)
        self.log(f"移动节点 {len(cmd.moves)} 个")
        self._after_edit(cmd)

    def _transform_nodes(self, mode):
        if not self._need_model():
            return
        nids = self.sel_nodes
        if not nids:
            QMessageBox.warning(self, APP_TITLE, "请先选择要变换的节点")
            return
        dlg = TransformDialog(self, self.model, nids, mode)
        if dlg.exec_() != QDialog.Accepted:
            return
        cmd = dlg.command()
        if cmd is None:
            self.log("变换无位移 (参数未改变坐标)")
            return
        self.model.apply(cmd)
        self.log(f"{mode}节点 {len(cmd.moves)} 个")
        self._after_edit(cmd)

    def add_node_dialog(self):
        if not self._need_model():
            return
        dlg = AddNodeDialog(self, self.model)
        if dlg.exec_() != QDialog.Accepted:
            return
        nid, xyz = dlg.values()
        if nid in self.model.nodes:
            QMessageBox.warning(self, APP_TITLE, f"节点 {nid} 已存在")
            return
        cmd = CmdAddNode(nid, xyz)
        self.model.apply(cmd)
        self.log(f"添加节点 {nid} @ ({xyz[0]:.6g}, {xyz[1]:.6g}, {xyz[2]:.6g})")
        self._after_edit(cmd)

    def add_element_dialog(self):
        if not self._need_model():
            return
        dlg = AddElementDialog(self, self.model)
        if dlg.exec_() != QDialog.Accepted:
            return
        eid, cfg, ids = dlg.values()
        missing = [i for i in ids if i not in self.model.nodes]
        if missing:
            QMessageBox.warning(self, APP_TITLE,
                                f"节点不存在: {missing[:10]}{'…' if len(missing) > 10 else ''}")
            return
        _name, nn, _cat = config_info(cfg)
        if nn and len(ids) != nn:
            r = QMessageBox.question(
                self, APP_TITLE,
                f"config {cfg} 标准节点数为 {nn}, 实际 {len(ids)}. 仍要创建吗?",
                QMessageBox.Yes | QMessageBox.No)
            if r != QMessageBox.Yes:
                return
        if not ids:
            return
        cmd = CmdAddElements([Elem(eid, list(ids), cfg)])
        self.model.apply(cmd)
        self.log(f"添加单元 eid={eid} config={cfg} 节点={ids}")
        self._after_edit(cmd)

    def delete_selected(self):
        if not self._need_model():
            return
        if self.sel_nodes:
            nids = sorted(self.sel_nodes)
            cmd = CmdDeleteNodes(self.model, nids)
            ne = len(cmd.elems)
            r = QMessageBox.question(
                self, APP_TITLE,
                f"删除 {len(nids)} 个节点将连带删除 {ne} 个单元. 继续?",
                QMessageBox.Yes | QMessageBox.No)
            if r != QMessageBox.Yes:
                return
            self.model.apply(cmd)
            self.log(f"删除节点 {len(nids)} 个 (连带单元 {ne} 个)")
            self._after_edit(cmd)
        elif self.sel_elems:
            cmd = CmdDeleteElements(self.model, self.sel_elems)
            self.model.apply(cmd)
            self.log(f"删除单元 {len(cmd.items)} 个")
            self._after_edit(cmd)

    def flip_selected(self):
        if not self._need_model() or not self.sel_elems:
            return
        bad = [i for i in self.sel_elems
               if config_info(self.model.elements[i].config)[2] not in ("2D", "?")]
        if bad:
            QMessageBox.warning(self, APP_TITLE,
                                f"翻转仅支持 2D 单元; 选中中含 {len(bad)} 个非 2D 单元")
            return
        cmd = CmdFlipElements(self.sel_elems)
        self.model.apply(cmd)
        self.log(f"翻转单元法向 {len(cmd.indices)} 个")
        self._after_edit(cmd)

    def renumber_node_dialog(self):
        if not self._need_model():
            return
        old = sorted(self.sel_nodes)[0] if len(self.sel_nodes) == 1 else 1
        dlg = RenumberDialog(self, "节点重编号", old,
                             self.model.next_free_node_id())
        if dlg.exec_() != QDialog.Accepted:
            return
        old, new = dlg.values()
        if old not in self.model.nodes:
            QMessageBox.warning(self, APP_TITLE, f"节点 {old} 不存在")
            return
        if new in self.model.nodes:
            QMessageBox.warning(self, APP_TITLE, f"节点 {new} 已存在")
            return
        cmd = CmdRenumberNode(old, new)
        self.model.apply(cmd)
        self.log(f"节点重编号: {old} -> {new}")
        self._after_edit(cmd)

    def renumber_element_dialog(self):
        if not self._need_model():
            return
        old = self.model.elements[sorted(self.sel_elems)[0]].id \
            if len(self.sel_elems) == 1 else 1
        dlg = RenumberDialog(self, "单元重编号 (同 eid 全部生效)", old,
                             self.model.next_free_elem_id())
        if dlg.exec_() != QDialog.Accepted:
            return
        old, new = dlg.values()
        if not any(e.id == old for e in self.model.elements):
            QMessageBox.warning(self, APP_TITLE, f"单元 {old} 不存在")
            return
        if any(e.id == new for e in self.model.elements):
            QMessageBox.warning(self, APP_TITLE, f"单元 {new} 已存在")
            return
        cmd = CmdRenumberElements(old, new)
        self.model.apply(cmd)
        self.log(f"单元重编号: {old} -> {new}")
        self._after_edit(cmd)

    def _fill_editor(self, rows):
        self.editor_table.setRowCount(len(rows))
        for i, (k, v) in enumerate(rows):
            self.editor_table.setItem(i, 0, QTableWidgetItem(str(k)))
            self.editor_table.setItem(i, 1, QTableWidgetItem(str(v)))

    # ---------------- 底部面板 / Mask / 帮助 ----------------
    def _on_page_changed(self, page):
        self._current_page = page
        self.page_label.setText(HM_PAGE_LABELS.get(page, page))
        self.statusBar().showMessage(f"{page} page")
        self.log(f"Panel page: {page}")

    def _on_panel_clicked(self, page, name):
        self.page_label.setText(f"{page} / {name}")
        self.statusBar().showMessage(f"{page} / {name}")
        key = name.lower().strip()
        implemented = {
            "nodes": self.add_node_dialog,
            "node edit": self.move_node_dialog,
            "temp nodes": self._toggle_temp_nodes,
            "distance": self._measure_distance,
            # HyperMesh 2019 Geom/points 面板专管 *createpoint / *createpoints 几何点;
            # 与 display points (展示用 marker) 概念不同.
            "points": self._toggle_geo,
            "point edit": self.select_geo_point_dialog,
            "length": self._measure_geo_length,
            "translate": self.move_node_dialog,
            "rotate": lambda: self._transform_nodes("rotate"),
            "reflect": lambda: self._transform_nodes("reflect"),
            "scale": lambda: self._transform_nodes("scale"),
            "numbers": self.select_by_id_dialog,
            "find": self.select_by_id_dialog,
            "renumber": self.renumber_element_dialog,
            "count": self._count_selection,
            "mask": self._mask_hide,
            "isolate": self._mask_isolate,
            "edit element": self.add_element_dialog,
            "elem types": self._show_elem_types,
            # M7.2 Laplacian smooth 骨架 (NYI-M7-1/3/4: automesh/tetramesh/hex 未实现)
            "smooth": self._apply_laplacian_smooth,
            # M8.2 Post contour 占位 (NYI-M8-1: .h3d/.res 解码需 hmbatch oracle)
            "contour": self._show_pseudo_contour,
            # M6 Card image 骨架 (NYI-M6-1: 真实卡数据需 hmbatch oracle)
            "card edit": self._show_card_templates_dialog,
            "control cards": self._show_card_templates_dialog,
        }
        fn = implemented.get(key)
        if fn is not None:
            self.log(f"{page} / {name}")
            fn()
        else:
            self._nyi(f"{page} / {name}")

    def _nyi(self, name):
        self.log(f"[NYI] {name} — panel from HyperMesh 2019, not implemented")
        self.statusBar().showMessage(f"{name}  (not implemented)")

    def _find_tool(self):
        q = (self.find_edit.text() or "").strip().lower()
        if not q:
            return
        for page, cols in HM_PANEL_PAGES.items():
            for col in cols:
                for name in col:
                    if q in name.lower():
                        self.panel_bar.set_page(page)
                        self._on_panel_clicked(page, name)
                        return
        self._nyi(f"search: {q}")

    def _toggle_temp_nodes(self):
        self.act_show_nodes.setChecked(not self.act_show_nodes.isChecked())
        self._toggle_nodes()

    def _measure_distance(self):
        if len(self.sel_nodes) < 2:
            self.log("distance: select 2+ nodes first")
            return
        nids = sorted(self.sel_nodes)[:2]
        a, b = self.model.nodes[nids[0]], self.model.nodes[nids[1]]
        d = ((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2) ** 0.5
        self.log(f"distance {nids[0]}-{nids[1]} = {d:.8g}")
        self.statusBar().showMessage(f"distance = {d:.8g}")

    def _measure_geo_length(self):
        """Geom / length 面板: 选中几何点 id 两两成对累计长度.

        HyperMesh 2019 该面板对 *lengthmark (lines) 求和, 但 line record 解码
        仍在 NYI-M4-2. 这里用几何点端点对 (按 id 排序后两两配对) 给出等价的
        "总长度"近似, 用 *lengthmark 选择集输入. 仅对 db 11.05 规整点有效.
        """
        if not self._need_model():
            return
        # 收集选中集 (节点优先; 若无节点则尝试几何点 id 输入框)
        if not self.sel_geo_points:
            from PyQt5.QtWidgets import QInputDialog
            text, ok = QInputDialog.getText(self, "Geom / length",
                "输入几何点 id (范围/逗号分隔), 例如 1,3,5-12:")
            if not ok or not text.strip():
                return
            ids = sorted(_parse_id_list(text))
            ids = [i for i in ids if i in self.model.geo_points]
        else:
            ids = sorted(self.sel_geo_points)
        if len(ids) < 2:
            self.log("length: 需要至少 2 个几何点 id")
            self.statusBar().showMessage("Geom / length: id 数 < 2")
            return
        # 两两配对 (HyperMesh 习惯: 按 id 升序, 相邻为一段)
        total = 0.0
        segs = []
        for a, b in zip(ids[0::2], ids[1::2]):
            pa, pb = self.model.geo_points[a], self.model.geo_points[b]
            d = ((pa.x - pb.x) ** 2 + (pa.y - pb.y) ** 2
                 + (pa.z - pb.z) ** 2) ** 0.5
            total += d
            segs.append((a, b, d))
        leftover = ids[len(segs) * 2:]
        # Entity Editor 摘要
        lines = [f"Geom / length: {len(segs)} 段, 总长 {total:.8g}"]
        if leftover:
            lines.append(f"  警告: {len(leftover)} 个 id 未配对 (奇数): {leftover[:10]}"
                         + ("..." if len(leftover) > 10 else ""))
        for a, b, d in segs[:200]:
            lines.append(f"  {a:>6} -> {b:<6}  L={d:.6f}")
        if len(segs) > 200:
            lines.append(f"  ... 共 {len(segs)} 段, 仅显示前 200")
        self.info.setPlainText("\n".join(lines))
        self.log(f"Geom / length: {len(segs)} 段, 总长 {total:.8g} "
                 f"(未配对 {len(leftover)})")
        self.statusBar().showMessage(f"Geom / length = {total:.8g}")

    def _count_selection(self):
        self.log(f"count: nodes={len(self.sel_nodes)} elems={len(self.sel_elems)} "
                 f"model nodes={0 if self.model is None else len(self.model.nodes)} "
                 f"elems={0 if self.model is None else len(self.model.elements)}")

    def _show_elem_types(self):
        if self.model is None:
            return
        lines = ["Element types in model:"]
        for cfg, cnt in sorted(self.model.config_groups().items()):
            name, nn, cat = config_info(cfg)
            lines.append(f"  {cfg}  {name}  [{cat}]  n={nn or 'var'}  count={cnt}")
        self.info.setPlainText("\n".join(lines))
        self.log("elem types listed in Entity Editor")

    def _show_card_templates_dialog(self):
        """Analysis / card edit 或 control cards 面板.

        M6.1 骨架: 列出已知卡片模板 (PSHELL/PSOLID/MAT1/CQUAD4),
        选中后渲染字段表 + BDF 8-char 对齐文本. 不解码真实卡数据 (NYI-M6-1).
        """
        try:
            from hmdecoder.hm_card import list_templates, get_template, card_summary_html
        except ImportError:
            QMessageBox.warning(self, APP_TITLE, "hm_card 模块未就绪")
            return
        tpls = list_templates()
        from PyQt5.QtWidgets import QInputDialog
        pick, ok = QInputDialog.getItem(self, "Card templates (M6.1 骨架)",
            "选择卡片模板:", tpls, 0, False)
        if not ok or not pick:
            return
        tpl = get_template(pick)
        # Entity Editor 渲染字段表 + BDF 文本
        html_lines = [f"<b>{tpl['long']}</b>"]
        html_lines.append("<table border=1 cellpadding=4 "
                          "style='border-collapse:collapse;font-family:monospace'>")
        html_lines.append("<tr><th>Field</th><th>Type</th><th>Description</th></tr>")
        for fname, ftype, desc in tpl["fields"]:
            html_lines.append(f"<tr><td><b>{fname}</b></td><td>{ftype}</td>"
                              f"<td>{desc}</td></tr>")
        html_lines.append("</table>")
        # BDF 8-char 字段对齐文本示例
        html_lines.append("<pre style='background:#f0f0f0;padding:6px'>"
                          f"{self._sample_bdf_text(pick)}</pre>")
        html_lines.append("<i style='color:#a00'>[NYI-M6-1] 真实卡数据解码需 "
                          "hwtemplex.dll + hmbatch oracle; 当前 skeleton 仅给字段骨架</i>")
        self.info.setHtml("<br>".join(html_lines))
        self.log(f"Card template: {pick}")
        self.statusBar().showMessage(f"Card: {pick} (template)")

    def _sample_bdf_text(self, name):
        """生成示例 BDF 文本, 用于卡片面板可视化."""
        try:
            from hmdecoder.hm_card import format_card_text
        except ImportError:
            return ""
        examples = {
            "PSHELL": {"PID": 1, "MID": 100, "T": 1.5},
            "PSOLID": {"PID": 2, "MID": 100, "IN": 0},
            "MAT1":   {"MID": 100, "E": 2.1e11, "G": 8.0e10,
                       "NU": 0.3, "RHO": 7850.0},
            "CQUAD4": {"EID": 1001, "PID": 1, "G1": 10, "G2": 11,
                       "G3": 12, "G4": 13},
        }
        return format_card_text(name, examples.get(name, {}))

    def _apply_laplacian_smooth(self):
        """2D / smooth 面板: Laplacian 平滑 (M7.2 骨架).

        NYI-M7-1: 2D automesh (需几何 record 解码) 未实现.
        NYI-M7-3: tetramesh (需 Delaunay 工业级内核) 未实现.
        当前实现: 基于现有单元拓扑 Laplacian 平滑 (不依赖几何 record).
        """
        if not self._need_model():
            return
        from PyQt5.QtWidgets import QInputDialog
        iters, ok = QInputDialog.getInt(self, "Laplacian smooth (M7.2)",
            "迭代次数 (建议 3-10):", 5, 1, 50, 1)
        if not ok:
            return
        try:
            from hmdecoder.mesher import laplacian_smooth_2d, smooth_quality_report
        except ImportError:
            QMessageBox.warning(self, APP_TITLE, "mesher 模块未就绪")
            return
        before = {nid: (n.x, n.y, n.z) for nid, n in self.model.nodes.items()}
        after = laplacian_smooth_2d(self.model, iterations=iters)
        # 报告到 Entity Editor
        lines = [
            f"Laplacian smooth: iterations={iters}",
            smooth_quality_report(self.model, before, after),
            "",
            "(NYI-M7-1/3/4: automesh/tetramesh/hex 仍未实现; "
            "当前为纯拓扑 Laplacian 平滑骨架, 不依赖几何 record)",
        ]
        self.info.setPlainText("\n".join(lines))
        self.log(f"Laplacian smooth: iters={iters}, "
                 f"interior_disp={smooth_quality_report(self.model, before, after)}")
        self.statusBar().showMessage(f"smooth: {iters} iter (preview only)")

    def _show_pseudo_contour(self):
        """Post / contour 面板: 伪 contour 演示 (M8.2 骨架).

        NYI-M8-1: .h3d/.res 结果文件解码未实现 (需第三方格式逆向).
        当前: 用节点坐标派生伪标量场 (距包围盒中心距离 / z_height / id_modulo),
        显示场量统计 + band 分布到 Entity Editor.
        """
        if not self._need_model():
            return
        try:
            from hmdecoder.hm_post import (
                pseudo_contour_field, color_band, field_stats, FIELD_MODES)
        except ImportError:
            QMessageBox.warning(self, APP_TITLE, "hm_post 模块未就绪")
            return
        from PyQt5.QtWidgets import QInputDialog
        mode, ok = QInputDialog.getItem(self, "Pseudo contour (M8.2 骨架)",
            "场量模式 (无结果文件时演示):", FIELD_MODES, 0, False)
        if not ok or not mode:
            return
        field = pseudo_contour_field(self.model, mode)
        bands = color_band(field, n_bands=10)
        from collections import Counter
        bd = sorted(Counter(bands.values()).items())
        lines = [
            f"Pseudo contour: mode={mode}",
            f"Field stats: {field_stats(field)}",
            f"Band distribution (10 bands): {bd}",
            "",
            "(NYI-M8-1: .h3d/.res 结果文件解码未实现; 当前为伪 contour 占位)",
            "(NYI-M8-2: section cut / deformed / vector 仍 NYI)",
        ]
        self.info.setPlainText("\n".join(lines))
        self.log(f"Post / contour: {mode} -> {field_stats(field)}")
        self.statusBar().showMessage(f"contour (pseudo): {mode}")

    def _mask_isolate(self):
        if self.model is None or not self.sel_elems:
            self.log("isolate: select elements first")
            return
        keep = {self._group_key(self.model.elements[i]) for i in self.sel_elems}
        for key, g in self._groups.items():
            on = key in keep
            g.visible = on
            g.actor.SetVisibility(on)
            color, _ = self._group_style.get(key, (None, True))
            self._group_style[key] = (color, on)
        self._rebuild_tree()
        self._render()
        self.log(f"isolate groups {sorted(map(str, keep))}")

    def _mask_hide(self):
        if self.model is None or not self.sel_elems:
            self.log("hide: select elements first")
            return
        hide = {self._group_key(self.model.elements[i]) for i in self.sel_elems}
        for key in hide:
            g = self._groups.get(key)
            if g is None:
                continue
            g.visible = False
            g.actor.SetVisibility(False)
            color, _ = self._group_style.get(key, (None, True))
            self._group_style[key] = (color, False)
        self._rebuild_tree()
        self._render()
        self.log(f"hide groups {sorted(map(str, hide))}")

    def _mask_show_all(self):
        for key, g in self._groups.items():
            g.visible = True
            g.actor.SetVisibility(True)
            color, _ = self._group_style.get(key, (None, True))
            self._group_style[key] = (color, True)
        self._rebuild_tree()
        self._render()
        self.log("show all components")

    def _mask_reverse(self):
        for key, g in self._groups.items():
            on = not g.visible
            g.visible = on
            g.actor.SetVisibility(on)
            color, _ = self._group_style.get(key, (None, True))
            self._group_style[key] = (color, on)
        self._rebuild_tree()
        self._render()

    def _show_user_profile(self):
        profiles = (
            "Abaqus (Explicit)", "Abaqus (Standard)", "OptiStruct",
            "Nastran", "LS-DYNA", "ANSYS", "Radioss",
        )
        cur = profiles.index(self._user_profile) if self._user_profile in profiles else 0
        name, ok = QInputDialog.getItem(
            self, "User Profile", "Solver profile:", profiles, cur, False)
        if ok and name:
            self._user_profile = name
            self._refresh_title()
            self.log(f"User profile: {name}")

    def _launch_hmopengl(self):
        exe = ALTAIR_ROOT / "hm" / "bin" / "win64" / "hmopengl.exe"
        if exe.is_file():
            os.startfile(str(exe))  # noqa: S606
        else:
            QMessageBox.information(self, APP_TITLE, f"Not found: {exe}")

    def _open_help_file(self, path):
        if Path(path).is_file():
            os.startfile(str(path))  # noqa: S606
        else:
            QMessageBox.information(self, APP_TITLE, f"Not found: {path}")

    def open_hm_ui_help(self):
        self._open_help_file(HM_HELP_UI)

    def open_hm_tutorials(self):
        self._open_help_file(
            ALTAIR_ROOT / "help" / "hm" / "topics" / "chapter_heads" / "tutorials_r.htm")

    def open_hm_panels(self):
        self._open_help_file(HM_HELP_PANELS)

    # ---------------- 帮助 ----------------
    def open_hm_help(self):
        self._open_help_file(ALTAIR_ROOT / "help" / "hm" / "index.htm")

    def open_hwd_help(self):
        self._open_help_file(ALTAIR_ROOT / "help" / "hwd" / "index.htm")

    def about_dialog(self):
        QMessageBox.about(
            self, f"About {APP_TITLE}",
            "<b>hm_gui.py</b> — HyperMesh-style .hm viewer / editor<br><br>"
            "Layout: Altair HyperMesh 2019 classic workspace "
            "(hmopengl.exe / help/hm User Interface)<br>"
            "Style: pphdecoding light CAE chrome + HM panel area<br>"
            "Parser: hmdecoder (oracle-verified against HyperMesh 2019)<br>"
            "Display: PyQt5 + VTK 9<br>"
            "Config table: templates/feoutput/hm/general<br><br>"
            "Save as .hmj or export INP / STEP / IGES / CSV.<br>"
            "Binary .hm is read-only; write-back is not supported.")

    # ---------------- 拖放 ----------------
    def dragEnterEvent(self, event):  # noqa: N802
        if event.mimeData().hasUrls():
            for u in event.mimeData().urls():
                if u.toLocalFile().lower().endswith((".hm", ".hm10", ".hmj")):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event):  # noqa: N802
        for u in event.mimeData().urls():
            p = u.toLocalFile()
            if p.lower().endswith((".hm", ".hm10", ".hmj")):
                self.open_path(p)
                break

    def closeEvent(self, event):  # noqa: N802
        if self.model is not None and self.model.dirty:
            r = QMessageBox.question(
                self, APP_TITLE, "有未保存的编辑, 确定退出?",
                QMessageBox.Yes | QMessageBox.No)
            if r != QMessageBox.Yes:
                event.ignore()
                return
        event.accept()


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
def main(argv=None):
    argv = argv if argv is not None else sys.argv
    QtCore.QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtCore.QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 9))
    path = None
    for a in argv[1:]:
        if not a.startswith("-") and Path(a).is_file():
            path = a
            break
    win = HmMainWindow(path)
    win.show()
    close_ms = os.environ.get("HM_GUI_TEST_CLOSE")
    if close_ms:
        QTimer.singleShot(int(close_ms), app.quit)
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
