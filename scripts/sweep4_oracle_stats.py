"""分析 oracle 批量计数: 各实体类型分布 + 按目录分组."""
import re, os
from collections import defaultdict

ents = ['nodes', 'elems', 'comps', 'mats', 'props', 'loads', 'loadcols', 'systems',
        'groups', 'sets', 'points', 'lines', 'surfs', 'solids', 'titles']
stat = defaultdict(lambda: defaultdict(int))  # dir -> ent -> files with >0
counts = defaultdict(lambda: defaultdict(int))  # dir -> ent -> total count
tot = defaultdict(int)  # dir -> files
readerr = []
for line in open('output/sweep4_oracle.log', encoding='utf-8', errors='replace'):
    line = line.rstrip()
    if not line.startswith('== '):
        continue
    parts = line.split(' | ')
    bname = parts[0].split('== ')[1]
    if parts[1] == 'READ-ERR':
        readerr.append((bname, parts[2][:80] if len(parts) > 2 else '?'))
        continue
    # 目录归属
    path = parts[1] if len(parts) == 2 else ''
    d = {}
    for p in parts[2:]:
        m = re.match(r'([a-z]+)=(-?[0-9]+)', p)
        if m:
            d[m.group(1)] = int(m.group(2))
    # 判断目录: 用 bname 无法直接区分, 从文件清单映射
    dirmap = {}
    for f in open('output/sweep4_files.txt', encoding='utf-8'):
        f = f.strip()
        if f:
            dirmap[os.path.basename(f)] = os.path.dirname(f).replace(chr(92), '/')
    dd = dirmap.get(bname, '?')
    dd = dd.split('/')[0] + '/' + dd.split('/')[1] + '/' + dd.split('/')[2] if '/' in dd else dd
    tot[dd] += 1
    for e in ents:
        if d.get(e, 0) > 0:
            stat[dd][e] += 1
            counts[dd][e] += d.get(e, 0)

print('=== 目录概况 ===')
for dd in sorted(tot):
    print('%s: %d files' % (dd, tot[dd]))

print()
print('=== 各实体 >0 的文件数 (按目录) ===')
hdr = '%-58s' % 'dir'
for e in ents:
    hdr += ' %-8s' % e
print(hdr)
for dd in sorted(tot):
    row = '%-58s' % dd
    for e in ents:
        row += ' %-8d' % stat[dd][e]
    print(row)
row = '%-58s' % 'TOTAL'
for e in ents:
    s = sum(stat[dd][e] for dd in stat)
    row += ' %-8d' % s
print(row)

print()
print('=== 总实体数 (按目录, 仅列 >0 项) ===')
for dd in sorted(tot):
    items = ['%s=%d' % (e, counts[dd][e]) for e in ents if counts[dd][e] > 0]
    print('%s: %s' % (dd, ' '.join(items)))

print()
print('=== READ-ERR ===')
for b, r in readerr:
    print('  %s: %s' % (b, r))
