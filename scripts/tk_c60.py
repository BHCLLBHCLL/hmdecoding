import sys,re
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/truck.hm')
c60=[e for e in m.elements if e.config==60]
print('truck cfg60 count:',len(c60))
for e in c60[:5]:
    print('  eid',e.id,'nodes',e.nodes)