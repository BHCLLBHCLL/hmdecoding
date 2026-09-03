import json
gt=json.load(open('output/ground_truth/corpus_gt.json'))
for k,v in gt.items():
    import os
    if os.path.basename(k)=='seatbelt.hm':
        print('seatbelt nodes:', v['counts']['nodes'],'elems:',v['counts']['elements'])
    if os.path.basename(k)=='SEAT_MODEL.hm':
        print('SEAT_MODEL nodes:', v['counts']['nodes'])