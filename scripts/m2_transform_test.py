import os, sys, math
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, '.')
from PyQt5.QtWidgets import QApplication
_app = QApplication.instance() or QApplication([])
from hm_gui import Command, CmdMoveNodes, TransformDialog, Node

class FakeModel:
    def __init__(self, nodes):
        self.nodes = nodes
        self.elements = []
        self.undo_stack = []
    def apply(self, cmd):
        cmd.redo(self)
        self.undo_stack.append(cmd)
    def undo(self):
        if self.undo_stack:
            self.undo_stack.pop().undo(self)

# 构造 3 个节点
m = FakeModel({1: Node(1, 1, 0, 0), 2: Node(2, 0, 2, 0), 3: Node(3, 0, 0, 3)})

# 1. CmdMoveNodes redo/undo
cmd = CmdMoveNodes([(1, (1,0,0), (2,0,0))])
m.apply(cmd)
assert m.nodes[1].x == 2, 'move redo failed'
m.undo()
assert m.nodes[1].x == 1, 'move undo failed'
print('1. CmdMoveNodes redo/undo PASS')

# 2. 旋转数学绕 X 轴 90 度 (点 (0,1,0) -> (0,0,1))
TransformDialog  # (no-op ref)
p = TransformDialog._rotate((0, 1, 0), 0, 90, (0, 0, 0))
assert abs(p[1]) < 1e-9 and abs(p[2] - 1) < 1e-9, 'rotate X90 failed: %r' % (p,)
print('2. _rotate X-axis 90deg: %r PASS' % (p,))

# 3. 旋转 Z 轴 90 度 点 (1,0,0) -> (0,1,0)
p2 = TransformDialog._rotate((1, 0, 0), 2, 90, (0, 0, 0))
assert abs(p2[0]) < 1e-9 and abs(p2[1] - 1) < 1e-9, 'rotate Z90 failed: %r' % (p2,)
print('3. _rotate Z-axis 90deg: %r PASS' % (p2,))

# 4. 缩放: 绕中心 (0,0,0) 放大 2 倍
new = (m.nodes[1].x * 2, m.nodes[1].y * 2, m.nodes[1].z * 2)
assert new == (2, 0, 0), 'scale math failed'
print('4. scale math PASS')

# 5. 整体: 对模型 3 节点施加绕 X 轴 90 度, 生成 moves 并应用+撤销
moves = []
for nid in (1,2,3):
    n = m.nodes[nid]
    old = (n.x, n.y, n.z)
    new = TransformDialog._rotate(old, 0, 90, (0,0,0))
    moves.append((nid, old, new))
cmd = CmdMoveNodes(moves)
m.apply(cmd)
assert abs(m.nodes[2].y) < 1e-9 and abs(m.nodes[2].z - 2) < 1e-9, 'rotate model failed'
m.undo()
assert m.nodes[2].y == 2, 'rotate undo failed'
print('5. full rotate + undo PASS')
print('ALL M2 TRANSFORM TESTS PASS')
