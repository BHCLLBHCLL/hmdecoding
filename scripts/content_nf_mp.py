import sys, os, json, re, multiprocessing as mp
sys.path.insert(0, 'hmdecoder')
gt = json.load(open('output/ground_truth/corpus_gt.json'))
elems_dir = 'output/ground_truth/elems'

def map_outfile(path):
    b = os.path.basename(path)
    pp = os.path.normpath(path).replace('\\', '/')
    parent = 'hm'
    if '/interfaces/lsdyna/' in pp: parent = 'lsdyna'
    if '/interfaces/abaqus/' in pp: parent = 'abaqus'
    if '/interfaces/samcef/' in pp: parent = 'samcef'
    f2 = os.path.join(elems_dir, (parent + '_') + b + '.elems.txt')
    if os.path.exists(f2): return f2
    f1 = os.path.join(elems_dir, b + '.elems.txt')
    if os.path.exists(f1): return f1
    return None

from decoder import decode

def work(path):
    ef = map_outfile(path)
    if not ef:
        return (path, 'NOEF')
    try:
        m = decode(path)
    except Exception as e:
        return (path, 'ERR', str(e))
    dec = {}
    for e in m.elements:
        dec.setdefault(e.id, []).append((e.config, tuple(e.nodes)))
    oracle = {}
    for line in open(ef, encoding='utf-8'):
        mm = re.match(r'E (\d+) cfg=(\d+) nodes=(.*)', line.strip())
        if mm:
            eid = int(mm.group(1)); cfg = int(mm.group(2))
            nds = tuple(x for x in (int(x) for x in mm.group(3).split()) if x != 0)
            oracle[eid] = (cfg, nds)
    sc = dc = dn = od = oo = 0
    for eid, (cfg, nds) in oracle.items():
        if eid not in dec:
            oo += 1; continue
        dcands = [d for d in dec[eid] if d[0] == cfg]
        if dcands:
            sc += 1
            if not any(d[1] == nds for d in dcands):
                dn += 1
        else:
            dc += 1
    for eid in dec:
        if eid not in oracle:
            od += 1
    return (path, sc, dc, dn, od, oo, len(oracle))

if __name__ == '__main__':
    paths = [p for p in list(gt) if os.path.exists(p)]
    with mp.get_context('spawn').Pool() as pool:
        res = pool.map(work, paths)
    perfect = 0; rows = []
    for r in res:
        if len(r) == 3 and r[1] == 'ERR':
            rows.append((r[0], 'ERR')); continue
        if len(r) == 2:
            continue
        _, sc, dc, dn, od, oo, t = r
        p = (sc == t and dc == 0 and dn == 0 and od == 0 and oo == 0)
        if p: perfect += 1
        else:
            rows.append((os.path.basename(r[0]), 'sc=%d dc=%d dn=%d od=%d oo=%d t=%d' % (sc, dc, dn, od, oo, t)))
    print('non-strict content PERFECT: %d/%d' % (perfect, len(paths)))
    for name, d in sorted(rows):
        print('  %s' % d, '|', name)
