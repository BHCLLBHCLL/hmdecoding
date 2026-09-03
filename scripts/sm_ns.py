import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
print('db:',struct.unpack_from('<d',p,4)[0])
ns=D.find_node_section(p)
print('find_node_section:', ns)
print('struct multi:', D.find_node_section_struct(p, multi=True))