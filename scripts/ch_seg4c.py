import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/channel_brkt_assem_analysis.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def d64(b,o): return struct.unpack_from('<d',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
sh=326009; cnt=3
print('seg4 @',sh,'header:', [hex(u32(p,sh+k*4)) for k in range(6)])
# try parse the record: eid 2432/2433/2434, config 60. Find CONST or structure.
# search region for the 3 records
print('u32 stream from sh+24:')
for off in range(24,120,4):
    print('  +%03d: %08x'%(off,u32(p,sh+off)))