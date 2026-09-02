import sys
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/interfaces/abaqus/abaqus_contactManager_2D_tutorial.hm')
dec={}
for e in m.elements:
    dec.setdefault(e.id,[]).append((e.config,tuple(e.nodes)))
for eid in [1,2,3,4,375,376,384,385]:
    print('eid',eid,'decoded:',dec.get(eid))