#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hm_gui 截图验证: 逐步定位版."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import vtk

import hm_gui as G
from hmdecoder import decode

STEP = sys.argv[1] if len(sys.argv) > 1 else "all"
MODEL = sys.argv[2] if len(sys.argv) > 2 else "WS_3.2_3d_tetra_finish.hm"
TAG = sys.argv[3] if len(sys.argv) > 3 else ""
print("STEP =", STEP, "MODEL =", MODEL, flush=True)

app = QApplication(sys.argv)
win = G.HmMainWindow()
win.show()

model = decode(MODEL)
win.model = G.EditableModel(model, source_path=MODEL)
print("model ready", flush=True)


def shoot():
    print("rebuild...", flush=True)
    win._rebuild_scene(fit=True)
    print("rebuild done", flush=True)
    win._render()
    print("render done", flush=True)
    if STEP == "rebuild":
        app.quit()
        return
    rw = win.vtk_widget.GetRenderWindow()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(rw)
    w2i.SetInputBufferTypeToRGBA()
    w2i.ReadFrontBufferOff()
    w2i.Update()
    print("w2i done", flush=True)
    wr = vtk.vtkPNGWriter()
    wr.SetFileName(f"output/_gui_shot{TAG}.png")
    wr.SetInputConnection(w2i.GetOutputPort())
    wr.Write()
    print(f"saved output/_gui_shot{TAG}.png", flush=True)
    if STEP == "shot":
        app.quit()
        return
    win._set_elem_selection(set(range(0, 2000, 7)), 0)
    print("select done", flush=True)
    win._render()
    w2i.Modified()
    w2i.Update()
    wr.SetFileName(f"output/_gui_shot{TAG}_sel.png")
    wr.Write()
    print(f"saved output/_gui_shot{TAG}_sel.png", flush=True)
    app.quit()


QTimer.singleShot(1500, shoot)
app.exec_()
print("clean exit", flush=True)
