import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
for j in [2917113,2917333]:
    rec=None
    for off in range(j-40,j+4,4):
        if is_const(u32(p,off)): rec=off
    print('eid20995 area, CONST @',rec)
    if rec:
        for off in range(0,56,4):
            print('  +%02d: %08x'%(off,u32(p,rec+off)))