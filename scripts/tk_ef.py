import sys,re
sys.path.insert(0,'hmdecoder')
from decoder import decode
# elem_filter: eid -> oracle node tuple
elem_filter={}
for line in open('output/ground_truth/elems/truck.hm.elems.txt',encoding='utf-8'):
    mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
    if mm:
        eid=int(mm.group(1))
        nds=tuple(x for x in (int(x) for x in mm.group(3).split()) if x!=0)
        elem_filter[eid]=nds
m=decode('C:/Program Files/Altair/2019/tutorials/hm/truck.hm', elem_filter=elem_filter)
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
sc=sn=0
for eid,(cfg,nds) in oracle.items():
    dc=[d for d in dec.get(eid,[]) if d[0]==cfg]
    if dc:
        sc+=1
        if any(d[1]==nds for d in dc): sn+=1
print('truck elem_filter: sc',sc,'sn',sn,'/',len(oracle))