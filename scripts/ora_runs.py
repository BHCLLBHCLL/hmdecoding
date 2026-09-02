import re
oracle={}
for line in open('output/ground_truth/joints_all.txt',encoding='utf-8'):
    mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
    if mm: oracle[int(mm.group(1))]=(int(mm.group(2)),)
eids=sorted(oracle)
print('oracle eid range:', eids[0], '..', eids[-1], 'count', len(eids))
# contiguous runs
runs=[]; s=eids[0]; p=eids[0]
for e in eids[1:]:
    if e!=p+1:
        runs.append((s,p)); s=e
    p=e
runs.append((s,p))
print('contiguous runs:')
for a,b in runs:
    print('  %d..%d (%d)'%(a,b,b-a+1))