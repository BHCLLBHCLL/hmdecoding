import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
segs=D.find_elem_segments(p)
for (sh,segid,c71,cnt,X,Y) in segs:
    # first CONST after sh
    cp=None
    for off in range(sh+16,sh+200,4):
        if is_const(u32(p,off)): cp=off; break
    eid=u32(p,cp+4) if cp else None
    print('segid=%d sh=%d cnt=%d X=%d Y=%d first_eid=%s'%(segid,sh,cnt,X,Y,eid))