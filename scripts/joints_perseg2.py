import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def is_const(v): return (v & 0xFFFF)==0x1FF5 and (v>>24)==0x70
segs=D.find_elem_segments(p)
for (sh,segid,c71,cnt,X,Y) in segs:
    # for Y=2 or Y=4, probe _parse_cfg55_mpc with a fake row_map (identity up to big count)
    row_count=7000
    row_map={i:i for i in range(1,row_count+1)}
    if X==3 and Y in (2,4,7):
        gm=D._parse_cfg55_mpc(p,sh,cnt,row_count,row_map)
        print(' segid=%d Y=%d cnt=%d mpc=%d'%(segid,Y,cnt,len(gm) if gm else 0))