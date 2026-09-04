import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/body_side_assembly.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
print('db:',struct.unpack_from('<d',p,4)[0])
segs=D.find_elem_segments(p)
for (sh,segid,c71,cnt,X,Y) in segs:
    print('  segid=%d cnt=%d X=%d Y=%d'%(segid,cnt,X,Y))