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
# sample compare eid 1..10 and 257..260
for eid in list(range(1,11))+[257,258,259,260,497,6072,6073]:
    o=oracle.get(eid)
    d=dec.get(eid)
    print('eid',eid,'oracle=',o,'decoded=',d)