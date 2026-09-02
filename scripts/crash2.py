import sys
sys.path.insert(0,'hmdecoder')
from decoder import decode
for f,l in [('C:/Program Files/Altair/2019/tutorials/hm/interfaces/abaqus/crash_tubes.hm','crash_tubes'),('C:/Program Files/Altair/2019/tutorials/hm/rail_crash.hm','rail_crash')]:
    m=decode(f)
    print(l, len(m.elements))