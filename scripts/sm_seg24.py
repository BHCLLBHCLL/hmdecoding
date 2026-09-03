import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
segs=D.find_elem_segments(p)
sh=[s[0] for s in segs if s[1]==24][0]
cnt=[s[3] for s in segs if s[1]==24][0]
print('seg24 @',sh,'cnt',cnt)
# find eid 20995 record: walk CONST records, find one whose eid field = 20995
rec=None
for off in range(sh+16,sh+cnt*200,4):
    if is_const(u32(p,off)):
        v=u32(p,off)
        # check eid fields nearby
        if u32(p,off+4)==20995 or u16(p,off+18)==20995 or u32(p,off+20)==20995:
            rec=off; break
print('eid20995 CONST @',rec)
if rec:
    for off in range(0,64,4):
        print('  +%02d: %08x  u16=%d'%(off,u32(p,rec+off),u16(p,rec+off)))