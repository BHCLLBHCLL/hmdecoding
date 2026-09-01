import sys,os,json
sys.path.insert(0,'hmdecoder')
from decoder import decode
gt=json.load(open('output/ground_truth/corpus_gt.json'))
effects=[]
cnt=0
for k,v in gt.items():
    if not os.path.exists(k): continue
    cnt+=1
    exp=v['counts']['nodes']
    try:
        m=decode(k)
    except Exception:
        print('ERR', os.path.basename(k)); continue
    ref=set()
    for e in m.elements: ref.update(e.nodes)
    node_ids=set(m.nodes.keys())
    unref=[nid for nid in node_ids if nid not in ref]
    single=(len(unref)==1)
    resid=[nid for nid in unref if (sum(1 for c_ in (m.nodes[nid].x,m.nodes[nid].y,m.nodes[nid].z) if c_==0)>=2 or single)]
    if resid:
        import os.path as op
        effects.append((op.basename(k), len(m.nodes), len(m.nodes)-len(resid), exp, len(resid), sorted(resid)[:6]))
print('processed',cnt,'effects',len(effects))
for e in effects:
    print('  %s: %d->%d exp=%d removed=%d ids=%s'%(e[0],e[1],e[2],e[3],e[4],e[5]))