import json
gt=json.load(open('output/ground_truth/corpus_gt.json'))
for k,v in gt.items():
    if 'solid_map' in k: print('SOLID_MAP', k, v['counts'])