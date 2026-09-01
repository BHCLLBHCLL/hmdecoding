import sys
sys.path.insert(0,'hmdecoder')
from decoder import decode
for fn,label in [('C:/Program Files/Altair/2019/tutorials/hm/icw_ex2.hm','icw_ex2'),('C:/Program Files/Altair/2019/tutorials/hm/icw_ex1.hm','icw_ex1'),('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm','seat_2'),('C:/Program Files/Altair/2019/tutorials/hm/truck.hm','truck'),('C:/Program Files/Altair/2019/tutorials/hm/car_section.hm','car_section'),('C:/Program Files/Altair/2019/tutorials/hm/solid_map.hm','solid_map')]:
    m=decode(fn)
    print('%s nodes=%d'%(label,len(m.nodes)))