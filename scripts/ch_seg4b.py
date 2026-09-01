import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/channel_brkt_assem_analysis.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
start=326009
print('search eid markers 0x980/0x981/0x982:')
for off in range(0,220,4):
    v=u32(p,start+off)
    if v in (0x980,0x981,0x982):
        print('  eid %08x at +%d'%(v,off))
print('dump +24..+104:')
for off in range(24,104,4):
    print('  +%d: %08x'%(off,u32(p,start+off)))