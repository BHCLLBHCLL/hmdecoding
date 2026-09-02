import json,os
from collections import defaultdict
gt=json.load(open('output/ground_truth/corpus_gt.json'))
by_base=defaultdict(list)
for k in gt:
    if os.path.exists(k): by_base[os.path.basename(k)].append(k)
dups={b:ps for b,ps in by_base.items() if len(ps)>1}
print('duplicate basenames:', len(dups))
for b,ps in dups.items():
    print(' ',b)
    for p in ps: print('     ->',p)