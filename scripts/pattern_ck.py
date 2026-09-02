import sys,os,json,re
sys.path.insert(0,'hmdecoder')
from decoder import decode
gt=json.load(open('output/ground_truth/corpus_gt.json'))
elems_dir='output/ground_truth/elems'
def map_outfile(path):
    b=os.path.basename(path)
    f1=os.path.join(elems_dir,b+'.elems.txt')
    if os.path.exists(f1): return f1
    for tag in ('lsdyna_','hm_'):
        f2=os.path.join(elems_dir,tag+b+'.elems.txt')
        if os.path.exists(f2): return f2
    return None
targets=['fe_only.hm','yoke.hm','SEAT_MODEL.hm','truck.hm','molding1.hm','dummy_positioner.hm','frame_assembly.hm']
for path,info in gt.items():
    b=os.path.basename(path)
    if b not in targets: continue
    ef=map_outfile(path)
    if not ef: continue
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
    # node count pattern: for matched eid, compare len(ora nodes) vs len(dec nodes)
    pats={}
    for eid,(cfg,nds) in oracle.items():
        dc=dec.get(eid)
        if not dc: continue
        dn=len(dc[0][1]) if dc[0][0]==cfg else -1
        on=len(nds)
        key=(cfg,on,dn)
        pats[key]=pats.get(key,0)+1
    top=sorted(pats.items(),key=lambda x:-x[1])[:6]
    print(b,':')
    for (cfg,on,dn),n in top:
        print('   cfg=%d ora_nodes=%d dec_nodes=%d count=%d'%(cfg,on,dn,n))