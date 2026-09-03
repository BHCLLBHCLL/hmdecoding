import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
# eid 20995 = 0x5203. @2724263 likely element record (not node table)
j=2724263
# find nearest CONST before
rec=None
for off in range(j-80,j+4,4):
    if is_const(u32(p,off)): rec=off
print('eid20995 element area, CONST @',rec)
if rec:
    for off in range(0,64,4):
        print('  +%02d: %08x'%(off,u32(p,rec+off)))