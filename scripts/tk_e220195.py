import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/truck.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
# find eid 220195 CONST record
eid=220195
for i in range(len(p)-24):
    if is_const(u32(p,i)) and (u32(p,i+4)==eid or u32(p,i+20)==eid or u16(p,i+18)==eid):
        print('eid220195 CONST @',i)
        for off in range(0,72,4):
            print('  +%02d: %08x'%(off,u32(p,i+off)))
        break