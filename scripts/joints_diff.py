import sys,os
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
from decoder import decode
m=decode(fn)
eids=sorted(m.elements.keys())
print('decoder eid count:', len(eids))
print('eids near tail:', [e for e in eids if e>=6050])
# oracle has 6068-6079; check which present in decoder
for e in range(6068,6080):
    print(' eid',e,'inset', e in m.elements)