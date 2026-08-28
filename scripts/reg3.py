
import sys
sys.path.insert(0, "hmdecoder")
from decoder import decode
for f in ['seat_start.hm', 'abaqus_contactManager_3D_tutorial.hm', 'joints.hm', 'seat_2.hm']:
    import os
    path = f'C:/Program Files/Altair/2019/tutorials/hm/{f}'
    if not os.path.exists(path):
        path = f'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/{f}'
    if not os.path.exists(path):
        path = f'C:/Program Files/Altair/2019/tutorials/hm/interfaces/abaqus/{f}'
    m = decode(path)
    print(f"{f}: nodes={len(m.nodes)} elems={len(m.elements)}")
