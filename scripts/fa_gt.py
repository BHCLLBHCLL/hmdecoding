import json
gt=json.load(open('output/ground_truth/corpus_gt.json'))
for k,v in gt.items():
    import os
    b=os.path.basename(k)
    if b in ('frame_assembly_1.hm','frame_assembly_3.hm'):
        print(b,'->',k,'counts',v['counts'])