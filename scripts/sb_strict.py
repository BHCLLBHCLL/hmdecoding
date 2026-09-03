import sys,re
sys.path.insert(0,'hmdecoder')
from decoder import decode
valid=sorted(int(x.strip()) for x in open('output/ground_truth/sm_nodes_all.txt',encoding='utf-8') if x.strip().isdigit())
m=decode('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seatbelt.hm', node_filter=set(valid))
dec={}
for e in m.elements:
    dec.setdefault(e.id,[]).append((e.config,tuple(e.nodes)))
oracle={}
for line in open('output/ground_truth/elems/seatbelt.hm.elems.txt',encoding='utf-8'):
    mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
    if mm:
        eid=int(mm.group(1)); cfg=int(mm.group(2))
        nds=tuple(x for x in (int(x) for x in mm.group(3).split()) if x!=0)
        oracle[eid]=(cfg,nds)
sc=sn=od=oo=0
for eid,(cfg,nds) in oracle.items():
    if eid not in dec:
        oo+=1; continue
    dc=[d for d in dec[eid] if d[0]==cfg]
    if dc:
        sc+=1
        if any(d[1]==nds for d in dc): sn+=1
for eid in dec:
    if eid not in oracle: od+=1
print('seatbelt strict-elems: sc',sc,'sn',sn,'/',len(oracle),'od',od,'oo',oo)