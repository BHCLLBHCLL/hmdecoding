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
    if segid in (11,25):
        print('=== segid=%d sh=%d cnt=%d Y=%d ==='%(segid,sh,cnt,Y))
        recs=[]; pos=sh+16; end=min(sh+500,len(p))
        while pos<end:
            if is_const(u32(p,pos)): recs.append(pos)
            pos+=4
        for k,cp in enumerate(recs[:6]):
            print('  rec%d @%d:'%(k,cp), ' '.join('%08x'%u32(p,cp+w*4) for w in range(14)))