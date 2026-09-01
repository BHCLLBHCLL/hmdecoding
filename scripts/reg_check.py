import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
for fn,label in [('C:/Program Files/Altair/2019/tutorials/hm/interfaces/ansys/chapter2_2.hm','chapter2_2'),('C:/Program Files/Altair/2019/tutorials/hm/truck.hm','truck'),('C:/Program Files/Altair/2019/tutorials/hm/car_section.hm','car_section')]:
    try:
        raw=open(fn,'rb').read()
        p=gzip.decompress(raw[0x0c:])
        ns=D.find_node_section(p)
        hi,count,base,stride,idoff,chain=ns
        row_map={}; row=0
        xoff=24 if stride==96 else 12
        for k in range(count):
            rec=base+k*stride
            nid=struct.unpack_from('<I',p,rec+idoff)[0]
            row+=1; row_map[row]=nid
        row_count=len(row_map)
        for (sh,segid,c71,cnt,X,Y) in D.find_elem_segments(p):
            m=D._parse_cfg55_mpc(p,sh,cnt,row_count,row_map)
            c=D._parse_v13c60(p,sh,cnt,row_count,row_map)
            if (m and len(m)>0) or (c and len(c)>0):
                print('%s segid=%d cnt=%d X=%d Y=%d  cfg55_mpc=%s  c60=%s'%(label,segid,cnt,X,Y, len(m) if m else 0, len(c) if c else 0))
    except Exception as ex:
        print(label, 'ERR', repr(ex))