import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/solid_map.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
from decoder import u32,u16,d64
# real node base=4396 (nid=12) and 334580 (nid=20); find [0x88] header before these
def is_header(i):
    return u32(p,i)==0x88 and 1<=u32(p,i+4)<=10000000
print('headers before base 4396 (node nid12):')
for i in range(max(0,4396-100),4396):
    if is_header(i):
        print('  header @%d count=%d'%(i,u32(p,i+4)))
print('headers before base 334580 (node nid20):')
for i in range(max(0,334580-100),334580):
    if is_header(i):
        print('  header @%d count=%d'%(i,u32(p,i+4)))