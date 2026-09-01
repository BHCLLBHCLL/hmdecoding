import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/channel_brkt_assem_analysis.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
segs=D.find_elem_segments(p)
sh=[s[0] for s in segs if s[1]==4][0]; cnt=[s[3] for s in segs if s[1]==4][0]
print('seg4 @',sh,'cnt',cnt)
recs=[]; pos=sh+16; end=min(sh+400,len(p))
while pos<end:
    if is_const(u32(p,pos)): recs.append(pos)
    pos+=4
for cp in recs[:3]:
    print(' @%d const=%08x eid@+4=%d:'%(cp,u32(p,cp),u32(p,cp+4)), ' '.join('%08x'%u32(p,cp+w*4) for w in range(12)))