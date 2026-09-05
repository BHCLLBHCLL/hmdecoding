import sys
sys.path.insert(0, 'hmdecoder')
from decoder import load_payload, _parse_collectors_v11, d64

p = load_payload(r'C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/frame_assembly_1.hm')
print('db_version =', d64(p, 4))
r = _parse_collectors_v11(p)
comps, mats, props, groups, others = r
print('comps (%d):' % len(comps))
for k in sorted(comps):
    print('  %d %s' % (k, comps[k]))
print('mats (%d):' % len(mats))
for k in sorted(mats):
    print('  %d %s' % (k, mats[k]))
print('props (%d):' % len(props))
for k in sorted(props):
    print('  %d %s' % (k, props[k]))
print('groups (%d):' % len(groups))
for k in sorted(groups):
    print('  %d %s' % (k, groups[k]))
print('others (%d):' % len(others))
for k in sorted(others):
    print('  %d %s' % (k, others[k]))
