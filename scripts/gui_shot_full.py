#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hm_gui 整窗截图: 验证树/菜单/停靠/状态栏 + 大模型性能."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QPoint
from PyQt5.QtGui import QImage, QPainter
import vtk
from vtk.util.numpy_support import vtk_to_numpy
import numpy as np

import hm_gui as G

MODEL = sys.argv[1] if len(sys.argv) > 1 else "WS_3.2_3d_tetra_finish.hm"
TAG = sys.argv[2] if len(sys.argv) > 2 else ""

app = QApplication(sys.argv)
win = G.HmMainWindow()
win.show()

t0 = time.time()


def grab():
    print(f"total load+render: {time.time()-t0:.1f}s", flush=True)
    # 展开树 + 模拟选中信息
    win.tree.expandAll()
    pix = win.grab()
    # QWidget.grab 无法捕获 OpenGL 内容, 把 VTK 帧缓冲贴回视口位置
    w = win.vtk_widget
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(w.GetRenderWindow())
    w2i.ReadFrontBufferOff()
    w2i.Update()
    img = w2i.GetOutput()
    dims = img.GetDimensions()
    arr = vtk_to_numpy(img.GetPointData().GetScalars())
    if arr is not None and dims[0] > 0:
        arr = arr.reshape(dims[1], dims[0], -1)
        arr = np.ascontiguousarray(np.flipud(arr))
        ncomp = arr.shape[2]
        fmt = QImage.Format_RGB888 if ncomp == 3 else QImage.Format_RGBA8888
        qimg = QImage(arr.data, dims[0], dims[1], ncomp * dims[0], fmt).copy()
        painter = QPainter(pix)
        painter.drawImage(w.mapTo(win, QPoint(0, 0)), qimg)
        painter.end()
    pix.save(f"output/_gui_full{TAG}.png")
    print(f"saved output/_gui_full{TAG}.png", flush=True)
    app.quit()


def after_load():
    # 等 loader 完成
    if win.model is None or (win.loader and win.loader.isRunning()):
        QTimer.singleShot(1000, after_load)
        return
    QTimer.singleShot(1500, grab)


win.open_path(MODEL)
QTimer.singleShot(1000, after_load)
app.exec_()
print("clean exit", flush=True)
