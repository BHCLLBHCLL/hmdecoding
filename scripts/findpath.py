import json
gt=json.load(open('output/ground_truth/corpus_gt.json'))
for k,v in gt.items():
    import os
    b=os.path.basename(k)
    if any(s in b for s in ['chapter2_2','car_section','truck']):
        print(b, '->', k)