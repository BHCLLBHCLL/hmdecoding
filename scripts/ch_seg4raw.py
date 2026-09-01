import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/channel_brkt_assem_analysis.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
print('seg4 region @326009, u32 stream:')
for off in range(0,160,4):
    v=u32(p,326009+off)
    print('  +%03d: %08x'%(off,v))