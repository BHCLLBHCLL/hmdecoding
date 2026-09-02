import sys,re
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/interfaces/abaqus/abaqus_contactManager_2D_tutorial.hm')
dec={}
for e in m.elements:
    dec.setdefault(e.id,[]).append((e.config,tuple(e.nodes)))
oracle={}
for line in open('output/ground_truth/abq2d_elems_all.txt',encoding='utf-8'):
    mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
    if mm:
        eid=int(mm.group(1)); cfg=int(mm.group(2))
        nds=tuple(x for x in (int(x) for x in mm.group(3).split()) if x!=0)
        oracle[eid]=(cfg,nds)
# diff_nds eids
diff=[]
for eid,(cfg,nds) in oracle.items():
    if eid in dec:
        dc=[d for d in dec[eid] if d[0]==cfg]
        if dc and not any(d[1]==nds for d in dc):
            diff.append((eid,nds,dc[0][1]))
print('diff_nds eids:', [d[0] for d in diff][:30])
for eid,ond,dnd in diff[:6]:
    print('  eid',eid,'oracle',ond,'decoded',dnd)
ora_only=sorted(set(oracle)-set(dec))
dec_only=sorted(set(dec)-set(oracle))
print('only_ora eids:', ora_only)
print('only_dec eids:', dec_only)