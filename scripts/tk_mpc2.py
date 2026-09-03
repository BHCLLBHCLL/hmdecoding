import sys,re
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/truck.hm')
dec={}
for e in m.elements:
    dec.setdefault(e.id,[]).append((e.config,tuple(e.nodes)))
oracle={}
for line in open('output/ground_truth/elems/truck.hm.elems.txt',encoding='utf-8'):
    mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
    if mm:
        eid=int(mm.group(1)); cfg=int(mm.group(2))
        nds=tuple(x for x in (int(x) for x in mm.group(3).split()) if x!=0)
        oracle[eid]=(cfg,nds)
n=0
for eid,(cfg,nds) in oracle.items():
    if cfg!=55: continue
    dc=[d for d in dec.get(eid,[]) if d[0]==55]
    if dc and dc[0][1]!=nds:
        print('eid',eid,'ora_nodes',len(nds),'dec_nodes',len(dc[0][1]))
        print('  ora',nds[:8])
        print('  dec',dc[0][1][:8])
        n+=1
        if n>=3: break