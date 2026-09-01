import sys,os
sys.path.insert(0,'hmdecoder')
from decoder import decode
files=[('solid_map','C:/Program Files/Altair/2019/tutorials/hm/solid_map.hm'),('molding1','C:/Program Files/Altair/2019/tutorials/hm/molding1.hm'),('chapter2_2','C:/Program Files/Altair/2019/tutorials/hm/interfaces/ansys/chapter2_2.hm'),('icw_ex1','C:/Program Files/Altair/2019/tutorials/hm/icw_ex1.hm'),('dummy_positioner','C:/Program Files/Altair/2019/tutorials/hm/v17/dummy_positioner.hm')]
for label,f in files:
    try:
        m=decode(f)
        print('%s nodes=%d'%(label,len(m.nodes)))
    except Exception as ex:
        print(label,'ERR',repr(ex))