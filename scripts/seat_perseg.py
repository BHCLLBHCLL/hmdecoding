import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
row_map,row_count=D.parse_nodes(p) if hasattr(D,'parse_nodes') else (None,0)
row_count=len(row_map) if row_map else 0
print("row_count",row_count)
segs=D.find_elem_segments(p)
for (sh,segid,c71,cnt,X,Y) in segs:
    got=None
    if X==3 and Y==2:
        got=D._parse_y2_c60(p,sh,cnt,row_count,row_map)
        if got is None:
            got=D._parse_a_type(p,sh,cnt,row_count,row_map)
        n=len(got) if got else 0
        print("segid=%d cnt=%d -> %d"%(segid,cnt,n))
