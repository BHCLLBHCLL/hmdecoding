import sys
sys.path.insert(0,'hmdecoder')
from decoder import decode
valid=sorted(int(x.strip()) for x in open('output/ground_truth/sm_nodes_all.txt',encoding='utf-8') if x.strip().isdigit())
m=decode('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm', node_filter=set(valid))
print('SEAT_MODEL nodes:',len(m.nodes),'elems:',len(m.elements))