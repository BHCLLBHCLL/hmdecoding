import sys,os,json,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,d64
gt=json.load(open('output/ground_truth/corpus_gt.json'))
# we need oracle node id lists; only have full lists for seat_2/car_section/solid_map.
# Instead: check whether zero-coord 52B records' nids are referenced by any element (sanity)
cases=[]
for k,v in gt.items():
    if not os.path.exists(k): continue
    try:
        raw=open(k,'rb').read()
        p=gzip.decompress(raw[0x0c:])
    except Exception:
        continue
    ns=D.find_node_section(p)
    if not ns: continue
    hi,count,base,stride,idoff,chain=ns
    if chain: continue  # focus on 52B-flat only
    zero=[]
    for kk in range(count):
        rec=base+kk*stride
        if rec+stride>len(p): break
        nid=u32(p,rec+idoff)
        x,y,z=d64(p,rec+12),d64(p,rec+20),d64(p,rec+28)
        if 1<=nid<=10000000 and x==0 and y==0 and z==0:
            zero.append(nid)
    if zero:
        import os.path as op
        cases.append((op.basename(k),count,v['counts']['nodes'],len(zero),sorted(zero)[:8]))
print('files with zero-coord 52B-flat records:', len(cases))
for c in cases:
    print('  %s: count=%d exp=%d zero_recs=%d ids=%s'%(c[0],c[1],c[2],c[3],c[4]))