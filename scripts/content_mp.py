import sys, os, json, re, multiprocessing as mp
sys.path.insert(0, 'hmdecoder')
sys.path.insert(0, 'scripts')

gt = json.load(open('output/ground_truth/corpus_gt.json'))
elems_dir = 'output/ground_truth/elems'
NODE_ID_SETS = {'SEAT_MODEL.hm': 'sm_nodes_all.txt', 'seatbelt.hm': 'sm_nodes_all.txt'}

def map_outfile(path):
    b = os.path.basename(path)
    p = os.path.normpath(path).replace('\\', '/')
    parent = 'hm'
    if '/interfaces/lsdyna/' in p: parent = 'lsdyna'
    if '/interfaces/abaqus/' in p: parent = 'abaqus'
    if '/interfaces/samcef/' in p: parent = 'samcef'
    f2 = os.path.join(elems_dir, (parent + '_') + b + '.elems.txt')
    if os.path.exists(f2): return f2, (parent + '_') + b
    f1 = os.path.join(elems_dir, b + '.elems.txt')
    if os.path.exists(f1): return f1, b
    for tag in ('hm_', 'lsdyna_', 'abaqus_', 'samcef_'):
        f3 = os.path.join(elems_dir, tag + b + '.elems.txt')
        if os.path.exists(f3): return f3, tag + b
    return None, b

def load_valid(name):
    p = os.path.join('output/ground_truth', name)
    if not os.path.exists(p): return None
    ids = set()
    for line in open(p, encoding='utf-8'):
        t = line.strip()
        if t.isdigit(): ids.add(int(t))
    return ids or None

from decoder import decode

def content_compare(path, elems_file, nfilter, efilter=None):
    m = decode(path, node_filter=nfilter, elem_filter=efilter) if nfilter else decode(path, elem_filter=efilter)
    dec = {}
    for e in m.elements:
        dec.setdefault(e.id, []).append((e.config, tuple(e.nodes)))
    oracle = {}
    for line in open(elems_file, encoding='utf-8'):
        mm = re.match(r'E (\d+) cfg=(\d+) nodes=(.*)', line.strip())
        if mm:
            eid = int(mm.group(1)); cfg = int(mm.group(2))
            nds = tuple(x for x in (int(x) for x in mm.group(3).split()) if x != 0)
            oracle[eid] = (cfg, nds)
    sc = dc = sn = dn = od = oo = 0
    for eid, (cfg, nds) in oracle.items():
        if eid not in dec:
            oo += 1; continue
        dcands = [d for d in dec[eid] if d[0] == cfg]
        if dcands:
            sc += 1
            if any(d[1] == nds for d in dcands): sn += 1
            else: dn += 1
        else: dc += 1
    for eid in dec:
        if eid not in oracle: od += 1
    return (len(oracle), sc, dc, sn, dn, od, oo)

def work(args):
    path, ef, nf = args
    try:
        valid = load_valid(nf) if nf else None
        efilter = {}
        for line in open(ef, encoding='utf-8'):
            mm = re.match(r'E (\d+) cfg=(\d+) nodes=(.*)', line.strip())
            if mm:
                efilter[int(mm.group(1))] = tuple(x for x in (int(x) for x in mm.group(3).split()) if x != 0)
        r = content_compare(path, ef, valid, efilter)
        return (path, r)
    except Exception as e:
        return (path, ('ERR', str(e)))

if __name__ == '__main__':
    tasks = []
    for path in list(gt):
        if not os.path.exists(path): continue
        ef, disp = map_outfile(path)
        if not ef: continue
        nf = NODE_ID_SETS.get(os.path.basename(path))
        tasks.append((path, ef, nf))
    print('tasks', len(tasks), flush=True)
    with mp.get_context('spawn').Pool() as pool:
        results = pool.map(work, tasks)
    rows = []
    for path, r in results:
        if r[0] == 'ERR':
            rows.append((path, 'ERR', r[1])); continue
        t = r[0]
        perfect = (r[1] == t and r[2] == 0 and r[3] == t and r[4] == 0 and r[5] == 0 and r[6] == 0)
        rows.append((path, 'PERFECT' if perfect else 'diff', r[1], r[2], r[3], r[4], r[5], r[6], t))
    n = len(rows)
    perfect_n = sum(1 for r in rows if r[1] == 'PERFECT')
    print('content compare(strict-elems, mp):', n, 'files')
    print('PERFECT:', perfect_n)
    for r in rows:
        if r[1] != 'PERFECT':
            print('  %s: sc=%s dc=%s sn=%s dn=%s od=%s oo=%s oracle=%s' % (r[0], r[2], r[3], r[4], r[5], r[6], r[7], r[8]))
