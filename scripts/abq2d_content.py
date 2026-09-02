import sys,re
sys.path.insert(0,'hmdecoder')
from decoder import decode
def content_ck(fn,gtpath,label):
    m=decode(fn)
    dec={}
    for e in m.elements:
        dec.setdefault(e.id,[]).append((e.config,tuple(e.nodes)))
    oracle={}
    for line in open(gtpath,encoding='utf-8'):
        mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
        if mm:
            eid=int(mm.group(1)); cfg=int(mm.group(2))
            nds=tuple(x for x in (int(x) for x in mm.group(3).split()) if x!=0)
            oracle[eid]=(cfg,nds)
    same_cfg=0; diff_cfg=0; same_nds=0; diff_nds=0; only_dec=0; only_ora=0
    for eid,(cfg,nds) in oracle.items():
        if eid not in dec:
            only_ora+=1; continue
        dc=[d for d in dec[eid] if d[0]==cfg]
        if dc:
            same_cfg+=1
            if any(d[1]==nds for d in dc): same_nds+=1
            else: diff_nds+=1
        else:
            diff_cfg+=1
    for eid in dec:
        if eid not in oracle: only_dec+=1
    print('%s: same_cfg=%d diff_cfg=%d same_nds=%d diff_nds=%d only_dec=%d only_ora=%d  (dec %d / ora %d)'%(label,same_cfg,diff_cfg,same_nds,diff_nds,only_dec,only_ora,len(set(dec)),len(oracle)))
content_ck('C:/Program Files/Altair/2019/tutorials/hm/interfaces/abaqus/abaqus_contactManager_2D_tutorial.hm','output/ground_truth/abq2d_elems_all.txt','abq2d')