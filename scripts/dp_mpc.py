import sys,re
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/dummy_positioner.hm')
dec={}
for e in m.elements:
    dec.setdefault(e.id,[]).append((e.config,tuple(e.nodes)))
oracle={}
for line in open('output/ground_truth/elems/dummy_positioner.hm.elems.txt',encoding='utf-8'):
    mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
    if mm:
        eid=int(mm.group(1)); cfg=int(mm.group(2))
        nds=tuple(x for x in (int(x) for x in mm.group(3).split()) if x!=0)
        oracle[eid]=(cfg,nds)
n=0
for eid,(cfg,nds) in oracle.items():
    if cfg!=55: continue
    dc=[d for d in dec.get(eid,[]) if d[0]==cfg]
    if dc and len(dc[0][1])!=len(nds):
        print('eid',eid,'oracle_nodes',len(nds),nds[:6],'decoded_nodes',len(dc[0][1]),dc[0][1][:6])
        n+=1
        if n>=4: break