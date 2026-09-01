import sys
sys.path.insert(0,'hmdecoder')
from decoder import decode
for f in ['C:/Program Files/Altair/2019/tutorials/hm/channel_brkt_assem_analysis.hm','C:/Program Files/Altair/2019/tutorials/hm/channel_brkt_assem_loading.hm']:
    m=decode(f)
    print(f.split('/')[-1], len(m.elements))