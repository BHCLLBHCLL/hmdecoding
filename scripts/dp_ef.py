import sys,re,os
sys.path.insert(0,'hmdecoder')
from decoder import decode
# dummy elem filter
f='output/ground_truth/elems/dummy_positioner.hm.elems.txt'
print('dummy elems file exists:',os.path.exists(f))
elem_filter={}
if os.path.exists(f):
    for line in open(f,encoding='utf-8'):
        mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
        if mm:
            elem_filter[int(mm.group(1))]=tuple(x for x in (int(x) for x in mm.group(3).split()) if x!=0)
print('elem_filter entries:',len(elem_filter))