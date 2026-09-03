import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/truck.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
# find segid 2000311 cfg55 record for eid 219946
segs=D.find_elem_segments(p)
sh=[s[0] for s in segs if s[1]==2000311][0]
anchor=None
for off in range(sh+16,sh+80,4):
    if is_const(u32(p,off)): anchor=off; break
print('seg2000311 anchor @',anchor)
rec=anchor
for k in range(4):
    tag55=u32(p,rec+52)>>16
    eid=(u16(p,rec+44)<<16)|u16(p,rec+42)
    if eid==219946 and tag55==567:
        print('cfg55 rec eid',eid,'n=u32@+56=%d master@+60=%d'%(u32(p,rec+56),u32(p,rec+60)))
        print('slaves @+72..:',[u32(p,rec+72+4*t) for t in range(18)])
        break
    rec+=76+4*u32(p,rec+56) if tag55==567 else 152