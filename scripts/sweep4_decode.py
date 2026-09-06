"""遍历 4 案例目录, 用 decoder 解码全部 .hm, 输出 JSON 统计 + 崩溃列表."""
import sys, os, json, time, traceback
sys.path.insert(0, 'hmdecoder')
from decoder import decode

DIRS = [
    r'C:/Program Files/Altair/2019/tutorials/hm',
    r'C:/Program Files/Altair/2019/demos/hm',
    r'C:/Program Files/Altair/2019/tutorials/hwsolvers',
    r'D:/training/hypermesh',
]

rows = []
t0 = time.time()
n = 0
for d in DIRS:
    if not os.path.isdir(d):
        print('MISSING DIR', d, flush=True)
        continue
    for root, _, files in os.walk(d):
        for f in sorted(files):
            if not f.lower().endswith('.hm'):
                continue
            path = os.path.join(root, f)
            n += 1
            try:
                m = decode(path)
                rows.append({
                    'path': path,
                    'db': m.db_version,
                    'nodes': len(m.nodes),
                    'elems': len(m.elements),
                    'comps': len(m.comps),
                    'mats': len(m.mats),
                    'props': len(m.props),
                    'groups': len(m.groups),
                    'others': len(m.others),
                    'elem_variant': m.element_variant,
                })
            except Exception as ex:
                rows.append({'path': path, 'crash': repr(ex)})
            if n % 20 == 0:
                print('progress %d files, %.0fs' % (n, time.time()-t0), flush=True)

out = 'output/sweep4_decode.json'
json.dump(rows, open(out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
crash = [r for r in rows if 'crash' in r]
nodz = [r for r in rows if 'crash' not in r and r['nodes'] == 0]
print('TOTAL %d files, %.0fs' % (n, time.time()-t0), flush=True)
print('crashes %d, zero-node %d' % (len(crash), len(nodz)), flush=True)
for r in crash:
    print('CRASH', r['path'], r['crash'], flush=True)
for r in nodz[:20]:
    print('ZERONODE', r['path'], 'db', r.get('db'), flush=True)
print('WROTE', out, flush=True)
