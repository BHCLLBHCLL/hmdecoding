import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/frame_assembly.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
# find 2nd, 3rd cfg56 records (next CONST after 2388857)
rec=2388857
for k in range(3):
    # next CONST
    nxt=None
    j=p.find(b'\xf5\x1f',rec+24,min(rec+200,len(p)-2))
    while j>=0:
        if is_const(u32(p,j)): nxt=j; break
        j=p.find(b'\xf5\x1f',j+1,min(rec+200,len(p)-2))
    if nxt is None: break
    rec=nxt
    v20=u32(p,rec+20)
    print('rec @%d flag@+20=%08x nslave@+24=%d master@+28=%d slaves@+52..=[%s]'%(rec,v20,u32(p,rec+24),u32(p,rec+28),','.join(str(u32(p,rec+52+4*t)) for t in range(4))))