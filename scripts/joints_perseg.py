import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/joints.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
from decoder import u32,u16,d64
ns=D.find_node_section(p)
hi,count,base,stride,idoff,chain=ns
row_map={}; row=0
xoff=24 if stride==96 else 12
for k in range(count):
    rec=base+k*stride
    nid=u32(p,rec+idoff)
    row+=1; row_map[row]=nid
row_count=len(row_map)
segs=D.find_elem_segments(p)
print('seg | X Y cnt | per-parser yields')
for (sh,segid,c71,cnt,X,Y) in segs:
    yields=[]
    if X==3:
        g1=D._parse_a_type(p,sh,cnt,row_count,row_map) ; yields.append(('a_type',len(g1) if g1 else 0))
        gm=D._parse_cfg55_mpc(p,sh,cnt,row_count,row_map) ; yields.append(('cfg55_mpc',len(gm) if gm else 0))
        if Y==0: g0=D._parse_y0_elems(p,sh,cnt,row_count,row_map); yields.append(('y0',len(g0) if g0 else 0))
        if Y==2: g2=D._parse_y2_c60(p,sh,cnt,row_count,row_map); yields.append(('y2_c60',len(g2) if g2 else 0))
        if Y==6: g6=D._parse_y6_c3(p,sh,cnt,row_count,row_map); yields.append(('y6_c3',len(g6) if g6 else 0))
        if Y==7: g7=D._parse_y7_elems(p,sh,cnt,row_count,row_map); yields.append(('y7',len(g7) if g7 else 0))
        if Y==4: g4=D._parse_y4_elems(p,sh,cnt,row_count,row_map); yields.append(('y4',len(g4) if g4 else 0))
        if Y==3: gg=D._parse_a_geom(p,sh,len(p),cnt,row_count,row_map); yields.append(('a_geom',len(gg) if gg else 0))
    else:
        b=D._parse_b_type(p,sh,cnt,row_count,row_map,Y); yields.append(('b_type',len(b) if b else 0))
        b2=D._parse_b_slots(p,sh,cnt,row_count,row_map,Y); yields.append(('b_slots',len(b2) if b2 else 0))
        b3=D._parse_b_u16rows(p,sh,cnt,row_count,row_map,Y); yields.append(('b_u16',len(b3) if b3 else 0))
    print(' segid=%d X=%d Y=%d cnt=%d  %s'%(segid,X,Y,cnt,'  '.join('%s=%d'%t for t in yields)))