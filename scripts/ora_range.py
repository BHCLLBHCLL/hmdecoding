import sys,re
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm')
dec={}
for e in m.elements:
    dec.setdefault(e.id,[]).append((e.config,tuple(e.nodes)))
oracle={}
for line in open('output/ground_truth/joints_all.txt',encoding='utf-8'):
    mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
    if mm:
        oracle[int(mm.group(1))]=(int(mm.group(2)),tuple(int(x) for x in mm.group(3).split()))
# eid 377-496 in oracle: what are they?
print('oracle eids 370..500:')
for eid in sorted(oracle):
    if 370<=eid<=500:
        c,n=oracle[eid]
        print('  eid',eid,'cfg',c,'nodes',n[:4])