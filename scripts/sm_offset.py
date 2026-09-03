import sys,re
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm')
dec={}
for e in m.elements:
    dec.setdefault(e.id,[]).append((e.config,tuple(e.nodes)))
oracle={}
for line in open('output/ground_truth/elems/SEAT_MODEL.hm.elems.txt',encoding='utf-8'):
    mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
    if mm:
        eid=int(mm.group(1)); cfg=int(mm.group(2))
        nds=tuple(x for x in (int(x) for x in mm.group(3).split()) if x!=0)
        oracle[eid]=(cfg,nds)
# check offset: for matched eid same cfg, compute oracle-dec node diff per node
offsets={}
for eid,(cfg,nds) in oracle.items():
    dc=[d for d in dec.get(eid,[]) if d[0]==cfg]
    if dc and len(dc[0][1])==len(nds):
        dnds=dc[0][1]
        for o,d in zip(nds,dnds):
            off=o-d
            offsets[off]=offsets.get(off,0)+1
print('node offset distribution (oracle - decoded):')
for off in sorted(offsets,key=lambda x:-offsets[x])[:8]:
    print('  +%d: %d'%(off,offsets[off]))