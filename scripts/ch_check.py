import sys
sys.path.insert(0,'hmdecoder')
from decoder import decode
files = {
  'channel':'C:/Program Files/Altair/2019/tutorials/hm/channel_brkt_assem_analysis.hm',
  'channel_loading':'C:/Program Files/Altair/2019/tutorials/hm/channel_brkt_assem_loading.hm',
}
for name,f in files.items():
    m=decode(f)
    eids=set(m.elements[i].id for i in range(len(m.elements)))
    print(name, 'count', len(m.elements), 'max_eid', max(eids), 'has 2426-2428:', [2426 in eids,2427 in eids,2428 in eids])