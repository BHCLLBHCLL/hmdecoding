import json,os
gt=json.load(open('output/ground_truth/corpus_gt.json'))
paths=[k for k,v in gt.items() if os.path.exists(k) and v['counts']['elements']>0]
# 排除已导出的 4 个 + 巨无霸 (20万+)
done={'joints.hm','seat_2.hm','abaqus_contactManager_2D_tutorial.hm','hook.hm'}
skip_big=[]
todo=[]
for p in paths:
    b=p.replace('\\','/').split('/')[-1]
    e=gt[p]['counts']['elements']
    if b in done: continue
    if e>=200000:
        skip_big.append(p); continue
    todo.append(p)
open('output/ground_truth/paths_todo.txt','w').write('\n'.join(todo))
open('output/ground_truth/paths_big.txt','w').write('\n'.join(skip_big))
print('todo',len(todo),'big(200k+)',len(skip_big))
for p in skip_big: print('  big:',p.split('/')[-1])