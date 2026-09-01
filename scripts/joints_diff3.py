import sys,os
sys.path.insert(0,'hmdecoder')
from decoder import decode
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
m=decode(fn)
eids=sorted({e.id for e in m.elements})
print('decoder eid count:', len(eids))
print('eids >=6050:', [e for e in eids if e>=6050])
print('configs near tail:', [(e.id,e.config) for e in m.elements if e.id>=6050])