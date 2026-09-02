import json,os
gt=json.load(open('output/ground_truth/corpus_gt.json'))
from collections import defaultdict
by_base=defaultdict(list)
for k in gt:
    if os.path.exists(k): by_base[os.path.basename(k)].append(k)
dups=[p for ps in by_base.values() if len(ps)>1 for p in ps]
print('\n'.join(dups))