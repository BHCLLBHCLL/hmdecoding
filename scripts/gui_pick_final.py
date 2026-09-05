#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hm_gui 最终交互测试: 单击/Ctrl多选/框选/节点拾取/删除/撤销/工程往返.

事件路径: QTest -> HmView(Qt 层) -> 信号 -> 主窗口拾取.
(VTK 交互器样式在左键按下后 GrabFocus, 交互器 AddObserver 的 release
观察者收不到事件, 因此必须走 Qt 层.)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtTest import QTest

import hm_gui as G

app = QApplication(sys.argv)
win = G.HmMainWindow()
win.show()
win.open_path("WS_3.2_3d_tetra_finish.hm")

# Qt 信号送达计数
sig_count = {"press": 0, "release": 0, "move": 0}
win.vtk_widget.sig_press.connect(lambda: sig_count.__setitem__("press", sig_count["press"] + 1))
win.vtk_widget.sig_release.connect(lambda: sig_count.__setitem__("release", sig_count["release"] + 1))
win.vtk_widget.sig_move.connect(lambda: sig_count.__setitem__("move", sig_count["move"] + 1))


def after_load():
    if win.model is None or (win.loader and win.loader.isRunning()):
        QTimer.singleShot(500, after_load)
        return
    QTimer.singleShot(2500, run)


def qclick(w, vx, vy, mod=Qt.NoModifier):
    """vx,vy 为 VTK 底朝上坐标."""
    QTest.mouseClick(w, Qt.LeftButton, mod,
                     QPoint(int(vx), int(w.height() - 1 - vy)), 50)


def run():
    w = win.vtk_widget
    W, H = w.width(), w.height()
    checks = []

    def ck(name, cond):
        checks.append((name, bool(cond)))
        if not cond:
            print(f"  [FAIL] {name}", flush=True)

    # 诊断: 宽屏视口下模型偏中央, 用 8/17,5/17 (已由 layout_dbg 确认命中)
    p = win._cell_picker
    direct = p.Pick(W * 8 / 17.0, H * 5 / 17.0, 0.0, win.renderer)
    print(f"diag: direct pick ret={direct} widget=({W},{H})", flush=True)

    # 1. 单击 (命中区 ix=8,iy=5)
    qclick(w, W * 8 / 17, H * 5 / 17)
    n1 = len(win.sel_elems)
    print(f"1. single click: {n1}  (sig press/release="
          f"{sig_count['press']}/{sig_count['release']})", flush=True)
    ck("t1 click", n1 == 1)
    ck("t1 sig", sig_count["press"] >= 1 and sig_count["release"] >= 1)

    # 2. Ctrl+单击另一位置 (ix=11, iy=5) 多选
    qclick(w, W * 11 / 17, H * 5 / 17, Qt.ControlModifier)
    n2 = len(win.sel_elems)
    print("2. ctrl click:", n2, flush=True)
    ck("t2 ctrl", n2 >= 1)

    # 3. 框选: 从 (0.2W,0.2H) 拖到 (0.8W,0.8H) (Qt 坐标)
    iren = w.GetRenderWindow().GetInteractor()
    win.interact_combo.setCurrentText("框选")
    print("  style:", iren.GetInteractorStyle().GetClassName(), flush=True)
    x0, y0 = int(W * 0.2), int(H - 1 - H * 0.2)
    x1, y1 = int(W * 0.8), int(H - 1 - H * 0.8)
    QTest.mousePress(w, Qt.LeftButton, Qt.NoModifier, QPoint(x0, y0), 30)
    for i in range(1, 11):
        QTest.mouseMove(w, QPoint(x0 + (x1 - x0) * i // 10,
                                  y0 + (y1 - y0) * i // 10), 20)
    QTest.mouseRelease(w, Qt.LeftButton, Qt.NoModifier, QPoint(x1, y1), 30)
    n3 = len(win.sel_elems)
    print("3. rubber band:", n3, flush=True)
    ck("t3 rubber", n3 > 100)
    win.interact_combo.setCurrentText("旋转")

    # 4. 删除选中 + 撤销 + 重做
    e0 = len(win.model.elements)
    win.delete_selected()
    e1 = len(win.model.elements)
    print(f"4. delete: {e0} -> {e1}", flush=True)
    ck("t4 del", e1 == e0 - n3)
    win.undo()
    ck("t4 undo", len(win.model.elements) == e0)
    win.redo()
    ck("t4 redo", len(win.model.elements) == e1)
    print("   undo/redo OK", flush=True)
    win.undo()

    # 5. 节点拾取
    win.target_combo.setCurrentText("节点")
    win.act_show_nodes.setChecked(True)
    win._toggle_nodes()
    win._render()
    qclick(w, W * 8 / 17, H * 5 / 17)
    n5 = len(win.sel_nodes)
    print("5. node click:", n5, list(win.sel_nodes)[:3], flush=True)
    ck("t5 node", n5 >= 1)

    # 6. 移动节点 (命令 + 撤销)
    if win.sel_nodes:
        nid = sorted(win.sel_nodes)[0]
        node = win.model.nodes[nid]
        old_x = node.x            # 注意: node 是引用, 必须先取出旧值
        cmd = G.CmdMoveNodes([(nid, (node.x, node.y, node.z),
                               (node.x + 10, node.y, node.z))])
        win.model.apply(cmd)
        win._after_edit(cmd)
        ck("t6 move", abs(win.model.nodes[nid].x - (old_x + 10)) < 1e-9)
        win.undo()
        ck("t6 undo", abs(win.model.nodes[nid].x - old_x) < 1e-9)
        print("6. move node + undo OK", flush=True)

    # 7. 保存/重开工程
    win.model.save_json("output/_rt.hmj")
    em2 = G.EditableModel.from_json("output/_rt.hmj")
    ck("t7 roundtrip", len(em2.elements) == len(win.model.elements))
    print("7. hmj roundtrip OK", flush=True)

    bad = [n for n, c in checks if not c]
    print("RESULT:", "ALL PASS" if not bad else f"FAILED: {bad}", flush=True)
    app.quit()


QTimer.singleShot(1000, after_load)
app.exec_()
