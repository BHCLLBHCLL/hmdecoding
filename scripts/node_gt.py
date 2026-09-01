import json
gt=json.load(open('output/ground_truth/corpus_gt.json'))
import os
for k,v in gt.items():
    b=os.path.basename(k)
    if any(s in b for s in ['solid_map','molding1','chapter2_2','icw_ex1']):
        print(b, v['counts']['nodes'])