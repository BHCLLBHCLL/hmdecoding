import sys
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm')
n=list(m.nodes.values())[0]
print('node type:', type(n))
print('node attrs:', [a for a in dir(n) if not a.startswith('_')])
print('sample node:', n.id, n.x, n.y, n.z)