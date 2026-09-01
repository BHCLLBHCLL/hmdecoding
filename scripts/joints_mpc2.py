import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
segs=D.find_elem_segments(p)
import struct as st
row_count=7000
row_map={i:i for i in range(1,row_count+1)}
for (sh,segid,c71,cnt,X,Y) in segs:
    if segid in (11,25):
        gm=D._parse_cfg55_mpc(p,sh,cnt,row_count,row_map)
        print(' segid=%d mpc=%d keys=%s'%(segid,len(gm) if gm else 0, sorted(gm.keys()) if gm else []))