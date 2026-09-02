import sys,os
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm')
n149=m.nodes[149]
same=[nid for nid,n in m.nodes.items() if nid!=149 and abs(n.x-n149.x)<1e-9 and abs(n.y-n149.y)<1e-9 and abs(n.z-n149.z)<1e-9]
print('seat_2 nid149 coords:', n149.x, n149.y, n149.z)
print('nodes with identical coords:', same)