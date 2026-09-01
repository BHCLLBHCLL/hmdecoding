import json
gt=json.load(open('output/ground_truth/corpus_gt.json'))
for k,v in gt.items():
    import os
    if os.path.basename(k)=='solid_map.hm':
        print('solid_map counts:', v['counts'])
        print('full keys:', list(v.keys()))