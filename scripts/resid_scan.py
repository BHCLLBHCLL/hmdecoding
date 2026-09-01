import sys,os,json
sys.path.insert(0,'hmdecoder')
from decoder import decode
gt=json.load(open('output/ground_truth/corpus_gt.json'))
effects=[]
for k,v in gt.items():
    if not os.path.exists(k): continue
    exp=v['counts']['nodes']
    try:
        m=decode(k)
    except Exception:
        continue
    ref=set()
    for e in m.elements: ref.update(e.nodes)
    node_ids=set(m.nodes.keys())
    unref=[nid for nid in node_ids if nid not in ref]
    single=(len(unref)==1)
    resid=[]
    for nid in unref:
        n=m.nodes[nid]
        zeros=sum(1 for c_ in (n.x,n.y,n.z) if c_==0)
        if zeros>=2 or single: resid.append(nid)
    new_n=len(m.nodes)-len(resid)
    if resid:
        import os.path as op
        effects.append((op.basename(k), len(m.nodes), new_n, exp, len(resid), sorted(resid)[:6]))
print('files where criterion removes nodes:', len(effects))
for e in effects:
    print('  %s: %d->%d exp=%d removed=%d ids=%s'%(e[0],e[1],e[2],e[3],e[4],e[5]))