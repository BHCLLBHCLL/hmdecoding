import sys,os
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm')
print("seat_2 decoded elems:", len(m.elements))
