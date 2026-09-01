import sys
sys.path.insert(0,'hmdecoder')
from decoder import decode
m=decode('C:/Program Files/Altair/2019/tutorials/hm/channel_brkt_assem_analysis.hm')
eids=set(e.id for e in m.elements)
# oracle elems=2431; find gaps by checking contiguous low range sum
# print eids 1..40 to see missing at start
print('count', len(eids))
present=[e for e in sorted(eids) if e<=600]
print('lowest 10 eids', sorted(eids)[:10])
# look for gaps in 1..2440
missing=[e for e in range(1,2441) if e not in eids]
print('missing count', len(missing))
print('first 30 missing', missing[:30])