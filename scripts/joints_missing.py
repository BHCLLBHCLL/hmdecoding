import sys
sys.path.insert(0,'hmdecoder')
from decoder import decode
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
m=decode(fn)
eids=set(e.id for e in m.elements)
import re
oracle={}
for line in open('output/ground_truth/joints_all.txt',encoding='utf-8'):
    mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
    if mm:
        eid=int(mm.group(1)); cfg=int(mm.group(2)); nds=[int(x) for x in mm.group(3).split()]
        oracle[eid]=(cfg,nds)
missing=[e for e in sorted(oracle) if e not in eids]
print('decoded', len(eids), 'oracle', len(oracle), 'missing', len(missing))
for e in missing:
    print('  eid',e,'cfg',oracle[e][0],'nodes',oracle[e][1])