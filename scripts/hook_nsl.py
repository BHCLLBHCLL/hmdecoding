import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/samcef/hook.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
# find hook 0x7050 anchor for eid 393067
sh=[s[0] for s in D.find_elem_segments(p) if s[1]==17][0]
recs=[]; pos=sh+16; end=min(sh+600,len(p))
while pos<end:
    if is_const(u32(p,pos)): recs.append(pos)
    pos+=4
for cp in recs:
    if u32(p,cp+4)==393067:
        print('anchor @',cp,'u16@+44=%d u16@+46=%d u16@+50=%d'%(u16(p,cp+44),u16(p,cp+46),u16(p,cp+50)))
        print('  first 12 slave slots u16@+62+4t:', [u16(p,cp+62+4*t) for t in range(12)])
        break