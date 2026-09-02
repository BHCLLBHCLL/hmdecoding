import json
gt=json.load(open('output/ground_truth/corpus_gt.json'))
total=0; big=[]
for k,v in gt.items():
    e=v['counts']['elements']
    total+=e
    if e>10000: big.append((k.split('/')[-1],e))
print('files',len(gt),'total elements',total)
print('big files (>10k):', sorted(big,key=lambda x:-x[1])[:20])