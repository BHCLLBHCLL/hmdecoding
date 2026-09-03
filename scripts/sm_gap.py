import sys
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm')
dec=sorted(m.nodes.keys())
# check gaps
gaps=[(dec[i-1],dec[i]) for i in range(1,len(dec)) if dec[i]!=dec[i-1]+1]
print('node id gaps:',gaps[:10],'total',len(gaps))
print('dec count',len(dec),'max',dec[-1])