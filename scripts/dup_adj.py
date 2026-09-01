import sys,os,gzip,struct
sys.path.insert(0,'hmdecoder')
import decoder as D
from decoder import u32,d64
for fn,label in [('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/seat_2.hm','seat_2'),('C:/Program Files/Altair/2019/tutorials/hm/car_section.hm','car_section')]:
    raw=open(fn,'rb').read()
    p=gzip.decompress(raw[0x0c:])
    ns=D.find_node_section(p)
    hi,count,base,stride,idoff,chain=ns
    # find adjacent records with identical coords (placeholder/duplicate-node)
    prev=None
    dup_adj=[]
    for k in range(count):
        rec=base+k*stride
        if rec+stride>len(p): break
        nid=u32(p,rec+idoff)
        x,y,z=d64(p,rec+12),d64(p,rec+20),d64(p,rec+28)
        cur=(round(x,4),round(y,4),round(z,4),nid)
        if prev and prev[:3]==cur[:3]:
            dup_adj.append((k-1,k,prev[3],cur[3],cur[:3]))
        prev=cur
    print('%s: adjacent-identical-coord pairs (k-1,k, nid_prev, nid_cur, xyz): %d'%(label,len(dup_adj)))
    for d in dup_adj[:6]:
        print('   ',d)