import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/channel_brkt_assem_analysis.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
sh=326009
print('record2 (eid 2433) +158..+276:')
for off in range(158,276,4):
    print('  @+%03d: %08x  u16[+%d]=%d u16[+%d]=%d'%(off,u32(p,sh+off),off,u16(p,sh+off),off+2,u16(p,sh+off+2)))