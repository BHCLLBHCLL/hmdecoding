import sys,re
sys.path.insert(0,'hmdecoder')
from decoder import decode
def ck(path,ef,label):
    m=decode(path)
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
    print('%s: sc=%d sn=%d/%d od=%d oo=%d'%(label,sc,sn,len(oracle),od,oo))
ck('C:/Program Files/Altair/2019/tutorials/hm/frame_assembly_3.hm','output/ground_truth/elems/hm_frame_assembly_3.hm.elems.txt','fa3')
ck('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_3.hm','output/ground_truth/elems/lsdyna_frame_assembly_3.hm.elems.txt','lsdyna_fa3')