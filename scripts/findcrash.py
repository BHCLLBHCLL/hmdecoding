import json
gt=json.load(open('output/ground_truth/corpus_gt.json'))
import os
for k,v in gt.items():
    b=os.path.basename(k)
    if 'crash' in b:
        print(b,'->',k, v['counts']['elements'])