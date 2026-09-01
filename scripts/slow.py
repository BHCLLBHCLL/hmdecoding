import sys,os,time
sys.path.insert(0,'hmdecoder')
from decoder import decode
import json
gt=json.load(open('output/ground_truth/corpus_gt.json'))
slow=[]
for k,v in gt.items():
    if not os.path.exists(k): continue
    t=time.time()
    try:
        m=decode(k)
    except Exception as ex:
        print('ERR',os.path.basename(k),ex); continue
    dt=time.time()-t
    if dt>2: slow.append((dt,os.path.basename(k),len(m.nodes)))
slow.sort(reverse=True)
print('slow files:')
for dt,name,n in slow[:12]:
    print('  %.2fs %s nodes=%d'%(dt,name,n))