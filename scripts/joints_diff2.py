import sys,os
sys.path.insert(0,'hmdecoder')
from decoder import decode
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
m=decode(fn)
eids=sorted({e[0] for e in m.elements})
print('decoder eid count:', len(eids))
print('eids near tail:', [e for e in eids if e>=6050])
for e in range(6068,6080):
    print(' eid',e,'inset', any(x[0]==e for x in m.elements))