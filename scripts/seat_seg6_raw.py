import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
sh=171576; cnt=32
print("seg @",sh,"header u32:",[hex(u32(p,sh+k*4)) for k in range(6)])
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
# find CONST after header
found=False
for pos in range(sh+16, min(sh+1200,len(p))-4, 4):
    v=u32(p,pos)
    if is_const(v):
        print("CONST @",pos,"next:", " ".join("%08x"%u32(p,pos+k*4) for k in range(20)))
        found=True
        break
if not found:
    print("no CONST near header; dump after header u32:")
    print("  ", " ".join("%08x"%u32(p,sh+24+k*4) for k in range(20)))
