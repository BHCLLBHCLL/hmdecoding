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
    if segid in (11,25,12,3):
        print('=== segid=%d sh=%d cnt=%d X=%d Y=%d ==='%(segid,sh,cnt,X,Y))
        recs=[]; pos=sh+16; end=min(sh+900,len(p))
        while pos<end:
            if is_const(u32(p,pos)): recs.append(pos)
            pos+=4
        for k,cp in enumerate(recs[:6]):
            print('  rec%d @%d const=%08x eid@+4=%d u16@+18=%d:'%(k,cp,u32(p,cp),u32(p,cp+4),u16(p,cp+18)), ' '.join('%08x'%u32(p,cp+w*4) for w in range(14)))