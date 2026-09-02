import os,glob,json
gt=json.load(open('output/ground_truth/corpus_gt.json'))
by_base={}
for k,v in gt.items(): by_base[os.path.basename(k)]=v['counts']['elements']
mismatch=[]
for f in glob.glob('output/ground_truth/elems/*.elems.txt'):
    b=os.path.basename(f).replace('.elems.txt','')
    first=open(f,encoding='utf-8').readline().strip()
    cnt=int(first.split('=')[1]) if '=' in first else -1
    exp=by_base.get(b)
    if exp is not None and cnt!=exp:
        mismatch.append((b,cnt,exp))
print('files exported:', len(glob.glob('output/ground_truth/elems/*.elems.txt')))
print('count mismatch:', mismatch)