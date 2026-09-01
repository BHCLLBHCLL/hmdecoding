import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
sh=171576
# walk CONST records in seg6 region
pos=sh+16
end=min(sh+2400,len(p))
c=[]
while pos<end:
    v=u32(p,pos)
    if is_const(v):
        c.append(pos)
    pos+=4
print("CONST count in seg6 window:", len(c))
for k,cp in enumerate(c[:20]):
    print("rec",k,"@%d"%cp, " ".join("%08x"%u32(p,cp+4*w) for w in range(14)))
