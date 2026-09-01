import sys,os,gzip
sys.path.insert(0,'hmdecoder')
import decoder as D
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/samcef/hook.hm'
raw=open(fn,'rb').read()
p=gzip.decompress(raw[0x0c:])
segs=D.find_elem_segments(p)
print('segs',len(segs))
for (sh,segid,c71,cnt,X,Y) in segs:
    print(' segid=%d cnt=%d X=%d Y=%d'%(segid,cnt,X,Y))