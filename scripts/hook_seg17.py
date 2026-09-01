import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/samcef/hook.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
sh=0
# segid 17 offset unknown; re-find
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
import sys
sys.path.insert(0,'hmdecoder')
import decoder as D
segs=D.find_elem_segments(p)
seg=[s for s in segs if s[1]==17][0]
sh=seg[0]
print('seg17 @',sh,'cnt',seg[3])
recs=[]
pos=sh+16; end=min(sh+400,len(p))
while pos<end:
    if is_const(u32(p,pos)): recs.append(pos)
    pos+=4
for k,cp in enumerate(recs[:8]):
    eid=u16(p,cp+18); cfg=u16(p,cp+30)-512
    print(' rec%d eid=%d cfg=%d words:'%(k,eid,cfg), ' '.join('%08x'%u32(p,cp+w*4) for w in range(10)))