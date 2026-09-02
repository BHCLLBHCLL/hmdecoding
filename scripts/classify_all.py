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
def classify(path,ef):
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
    n_trunc=0; n_shift=0; n_eid=0
    for eid,(cfg,nds) in oracle.items():
        dc=dec.get(eid)
        if not dc:
            n_eid+=1; continue
        matched=[d for d in dc if d[0]==cfg]
        if not matched:
            n_eid+=1; continue
        d=matched[0]
        if len(d[1])!=len(nds):
            n_trunc+=1
        elif d[1]!=nds:
            n_shift+=1
    return (n_trunc,n_shift,n_eid)
cats={'trunc':[],'shift':[],'eid':[],'perfect':[]}
for path,info in gt.items():
    if not os.path.exists(path): continue
    ef=map_outfile(path)
    if not ef: continue
    try:
        t,s,e=classify(path,ef)
    except Exception:
        continue
    b=os.path.basename(path)
    if t+s+e==0: cats['perfect'].append(b)
    elif e>0 and t==0 and s==0: cats['eid'].append((b,e))
    elif t>0: cats['trunc'].append((b,t))
    elif s>0: cats['shift'].append((b,s))
print('PERFECT:', len(cats['perfect']))
print('TRUNC:', len(cats['trunc']), sum(x[1] for x in cats['trunc']))
print('SHIFT:', len(cats['shift']), sum(x[1] for x in cats['shift']))
print('EID:', len(cats['eid']), sum(x[1] for x in cats['eid']))
print('--TRUNC files:')
for b,t in sorted(cats['trunc'],key=lambda x:-x[1])[:12]: print('   %s: %d'%(b,t))
print('--SHIFT files:')
for b,s in sorted(cats['shift'],key=lambda x:-x[1])[:12]: print('   %s: %d'%(b,s))
print('--EID files:')
for b,e in sorted(cats['eid'],key=lambda x:-x[1])[:12]: print('   %s: %d'%(b,e))