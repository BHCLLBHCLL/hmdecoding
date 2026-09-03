import sys,re
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/frame_assembly.hm')
dec={}
for e in m.elements:
    dec.setdefault(e.id,[]).append((e.config,tuple(e.nodes)))
oracle={}
for line in open('output/ground_truth/elems/frame_assembly.hm.elems.txt',encoding='utf-8'):
    mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
    if mm:
        eid=int(mm.group(1)); cfg=int(mm.group(2))
        nds=tuple(x for x in (int(x) for x in mm.group(3).split()) if x!=0)
        oracle[eid]=(cfg,nds)
# sample cfg56 elements, oracle vs decoded
n=0
for eid,(cfg,nds) in oracle.items():
    if cfg!=56: continue
    dc=[d for d in dec.get(eid,[]) if d[0]==cfg]
    if dc and dc[0][1]!=nds:
        print('eid',eid,'oracle',nds,'decoded',dc[0][1])
        n+=1
        if n>=5: break
# also count how many cfg56 with correct len
ok_len=sum(1 for eid,(cfg,nds) in oracle.items() if cfg==56 and not any(len(d[1])==len(nds) for d in dec.get(eid,[]) if d[0]==56) if False else 1 if cfg==56 else 0)
print('total cfg56 oracle elements:', sum(1 for c,n in oracle.values() if c==56))