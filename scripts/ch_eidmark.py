import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/channel_brkt_assem_analysis.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def d64(b,o): return struct.unpack_from('<d',b,o)[0]
sh=326009
# candidate record starts: find eid markers 0x980(2432),0x981(2433),0x982(2434)
for off in range(24,400,4):
    v=u32(p,sh+off)
    if v in (0x980,0x981,0x982):
        print('eid %08x at +%d'%(v,off))
# also u16 markers
print('--- u16 markers ---')
for off in range(24,400,2):
    v=u16(p,sh+off)
    if v in (0x980,0x981,0x982):
        print('eid u16 %04x at +%d'%(v,off))