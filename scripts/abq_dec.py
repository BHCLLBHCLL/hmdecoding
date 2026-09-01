import sys,os
sys.path.insert(0,'hmdecoder')
from decoder import decode
import gzip,struct
fn='C:/Program Files/Altair/2019/tutorials/hm/interfaces/abaqus/abaqus_contactManager_2D_tutorial.hm'
m=decode(fn)
print("decoded elems:", len(m.elements))
# per-node comparison would need gt; just print count
