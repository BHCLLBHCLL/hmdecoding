import sys
sys.path.insert(0,'hmdecoder')
from decoder import decode
for f,l in [('C:/Program Files/Altair/2019/tutorials/hm/truck.hm','truck'),('C:/Program Files/Altair/2019/tutorials/hm/car_section.hm','car_section'),('C:/Program Files/Altair/2019/tutorials/hm/interfaces/ansys/chapter2_2.hm','chapter2_2'),('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm','joints')]:
    m=decode(f)
    print(l, len(m.elements), len(m.nodes))