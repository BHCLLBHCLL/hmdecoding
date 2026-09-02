import json,os
gt=json.load(open('output/ground_truth/corpus_gt.json'))
big=[k for k,v in gt.items() if os.path.exists(k) and v['counts']['elements']>=200000]
print('\n'.join(big))