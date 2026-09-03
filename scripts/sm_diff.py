import sys
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm')
dec=sorted(m.nodes.keys())
oracle=[int(x.strip()) for x in open('output/ground_truth/sm_nodes_all.txt',encoding='utf-8') if x.strip().isdigit()]
print('dec node ids: first',dec[0],'last',dec[-1],'count',len(dec))
print('oracle node ids: first',oracle[0],'last',oracle[-1],'count',len(oracle))
# check 17500-17530 range
print('dec 17500-17530:',[x for x in dec if 17500<=x<=17530])
print('ora 17500-17530:',[x for x in oracle if 17500<=x<=17530])
.join('') if False else 0