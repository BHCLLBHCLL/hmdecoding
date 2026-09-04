import sys,re
sys.path.insert(0,'hmdecoder')
from decoder import decode
def ck(path,ef,label,nf=None,eflt=None):
    m=decode(path, node_filter=nf, elem_filter=eflt)
    dec={}
    for e in m.elements:
        dec.setdefault(e.id,[]).append((e.config,tuple(e.nodes)))
    oracle={}
    for line in open(ef,encoding='utf-8'):
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
    print('%s: sc %d sn %d/%d od %d oo %d'%(label,sc,sn,len(oracle),od,oo))
def load_ef(f):
    eflt={}
    for line in open(f,encoding='utf-8'):
        mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
        if mm:
            eflt[int(mm.group(1))]=tuple(x for x in (int(x) for x in mm.group(3).split()) if x!=0)
    return eflt
# truck with elem_filter
ef_t=load_ef('output/ground_truth/elems/truck.hm.elems.txt')
ck('C:/Program Files/Altair/2019/tutorials/hm/truck.hm','output/ground_truth/elems/truck.hm.elems.txt','truck(ef)',None,ef_t)