import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
for fn in ['C:/Program Files/Altair/2019/tutorials/hm/keyhole.hm','C:/Program Files/Altair/2019/tutorials/hm/channel_brkt_assem_analysis.hm']:
    print('===',fn.split('/')[-1],'===')
    raw=open(fn,'rb').read()
    p=gzip.decompress(raw[0x0c:])
    def u16(b,o): return struct.unpack_from('<H',b,o)[0]
    def u32(b,o): return struct.unpack_from('<I',b,o)[0]
    def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
    segs=D.find_elem_segments(p)
    # find small Y=1 seg with cnt<=5 and config-5 records
    for (sh,segid,c71,cnt,X,Y) in segs:
        if cnt<=5 and X==3:
            recs=[]; pos=sh+16; end=min(sh+400,len(p))
            while pos<end:
                if is_const(u32(p,pos)): recs.append(pos)
                pos+=4
            print(' segid=%d cnt=%d Y=%d'%(segid,cnt,Y))
            for cp in recs[:3]:
                print('   @%d const=%08x eid@+4=%d flag@+22=%d &0xFF=%d nodes@+24=%s'%(cp,u32(p,cp),u32(p,cp+4),u16(p,cp+22),u16(p,cp+22)&0xff,[u32(p,cp+24+4*t) for t in range(4)]))