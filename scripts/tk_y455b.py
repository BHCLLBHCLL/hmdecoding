import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/truck.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
rec=23091140
for k in range(3):
    tag55=u32(p,rec+52)>>16
    eid=(u16(p,rec+44)<<16)|u16(p,rec+42)
    print('rec',k,'@',rec,'tag55',tag55,'eid',eid,'n@+56',u32(p,rec+56),'master@+60',u32(p,rec+60))
    print('   slaves@+72:',[u32(p,rec+72+4*t) for t in range(6)])
    rec += (76+4*u32(p,rec+56)) if tag55==567 else 152