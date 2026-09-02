import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,u16,d64
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
end=base+count*stride
print('seat_2 node section: base=%d count=%d end=%d'%(base,count,end))
print('after node section (u32):')
for off in range(end,end+80,4):
    print('  @%d: %08x'%(off,u32(p,off)))