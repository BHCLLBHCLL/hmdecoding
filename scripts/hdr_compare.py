import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,u16,d64
files=[('seat_2','C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm',1620),('seat_start','C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_start.hm',1620),('truck','C:/Program Files/Altair/2019/tutorials/hm/truck.hm',212138),('car_section','C:/Program Files/Altair/2019/tutorials/hm/car_section.hm',26695),('solid_map','C:/Program Files/Altair/2019/tutorials/hm/solid_map.hm',2),('icw_ex1','C:/Program Files/Altair/2019/tutorials/hm/icw_ex1.hm',89),('keyhole','C:/Program Files/Altair/2019/tutorials/hm/keyhole.hm',550),('hook','C:/Program Files/Altair/2019/tutorials/hm/interfaces/samcef/hook.hm',14069)]
for label,fn,exp in files:
    raw=open(fn,'rb').read()
    p=gzip.decompress(raw[0x0c:])
    ns=D.find_node_section(p)
    if not ns:
        print(label,'no ns'); continue
    hi,count,base,stride,idoff,chain=ns
    # dump header 16 u32
    hdr=[u32(p,hi+k*4) for k in range(10)]
    print('%s: hi=%d count=%d(exp=%d) stride=%d chain=%s'%(label,hi,count,exp,stride,chain))
    print('    hdr=', ['%08x'%v for v in hdr])