import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/truck.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
# find segid 2000189, its cfg60 record (eid 220195)
segs=D.find_elem_segments(p)
sh=[s[0] for s in segs if s[1]==2000189][0]
print('seg2000189 @',sh)
anchor=None
for off in range(sh+16,sh+80,4):
    if is_const(u32(p,off)): anchor=off; break
print('anchor @',anchor)
rec=anchor
for k in range(3):
    tag60=u32(p,rec+68)>>16
    if tag60==316:
        eid=(u16(p,rec+60)<<16)|u16(p,rec+58)
        print('cfg60 rec eid',eid,'nodes@[72,76,164]=%d,%d,%d'%(u32(p,rec+72),u32(p,rec+76),u32(p,rec+164)))
        break
    rec+=176