import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/frame_assembly.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
# eid 9167 = 0x23CD. find in element records (with CONST anchor)
for i in range(len(p)-4):
    if u32(p,i)==9167 and is_const(u32(p,i-0)) if False else False: pass
# search CONST records whose @+4 or @+10 == 9167
pos=[]
for i in range(len(p)-24):
    if is_const(u32(p,i)):
        if u32(p,i+4)==9167 or u16(p,i+18)==9167 or u32(p,i+20)==9167:
            pos.append(i)
print('eid9167 CONST positions:',pos[:5])