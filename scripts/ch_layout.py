import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/channel_brkt_assem_analysis.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
sh=326009
# verify layout across 3 records: eid@rec, node1=u16@+14, node2=u16@+18
for rec in (40,158,276):
    eid=u32(p,sh+rec)
    n1=u16(p,sh+rec+14)
    n2=u16(p,sh+rec+18)
    print('rec@+%d eid=%d node1_row=%d node2_row=%d'%(rec,eid,n1,n2))