import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/samcef/hook.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
cp=731898
# count nodes from master @+40 until 0
n=0
while cp+40+4*n+4<=len(p) and u32(p,cp+40+4*n)!=0: n+=1
print('nodes from +40 until 0:', n)
print('node rows:', [u32(p,cp+40+4*t) for t in range(min(n,20))])
# eid check
print('eid u32@+4 =',u32(p,cp+4))
print('flag u16@+22 =',u16(p,cp+22),' config=',u16(p,cp+22)-256)