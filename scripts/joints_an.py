import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
# analyze each record in seg11(127516..128196) and seg25(128196..128588)
def analyse(sh,label):
    recs=[]; pos=sh+16; end=sh+700
    while pos<end:
        if is_const(u32(p,pos)): recs.append(pos)
        pos+=4
    for cp in recs:
        const=u32(p,cp)
        cv=const>>16
        print('%s @%d const=%08x top=%04x eid@+4=%d'%(label,cp,const,cv,u32(p,cp+4)), end=' ')
        if cv in (0x7024,0x7054):
            print('flag@+22&0xFF=%d flag@+30-512=%d flag@+34-512=%d'%(u16(p,cp+22)&0xff,u16(p,cp+30)-512,u16(p,cp+34)-512))
        elif cv==0x7050:
            print('u16@+44=%d u16@+46=%d flag=u16@+44-512=%d'%(u16(p,cp+44),u16(p,cp+46),u16(p,cp+44)-512))
        else:
            print()
analyse(127516,'seg11')
analyse(128196,'seg25')