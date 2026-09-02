import sys,re
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm')
dec={}
for e in m.elements:
    dec.setdefault(e.id,[]).append((e.config,tuple(e.nodes)))
oracle={}
for line in open('output/ground_truth/joints_all.txt',encoding='utf-8'):
    mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
    if mm:
        oracle[int(mm.group(1))]=(int(mm.group(2)),tuple(int(x) for x in mm.group(3).split()))
dec_only=sorted(set(dec)-set(oracle))
ora_only=sorted(set(oracle)-set(dec))
print('dec eids not in oracle:', len(dec_only), dec_only[:20], '...', dec_only[-5:])
print('oracle eids not in dec:', len(ora_only), ora_only[:20], '...', ora_only[-5:])
print('dec distinct', len(set(dec)), 'oracle distinct', len(set(oracle)), 'dec total records', len(m.elements))