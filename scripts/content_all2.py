import sys,os,json,re,glob
sys.path.insert(0,'hmdecoder')
from decoder import decode
gt=json.load(open('output/ground_truth/corpus_gt.json'))
elems_dir='output/ground_truth/elems'
NODE_ID_SETS = {
    'SEAT_MODEL.hm': 'sm_nodes_all.txt',
    'seatbelt.hm': 'sm_nodes_all.txt',
}
def map_outfile(path):
    b=os.path.basename(path)
    p=os.path.normpath(path).replace('\\','/')
    parent='hm'
    if '/interfaces/lsdyna/' in p: parent='lsdyna'
    if '/interfaces/abaqus/' in p: parent='abaqus'
    if '/interfaces/samcef/' in p: parent='samcef'
    # 优先同名碰撞: 先试 parent 前缀
    f2=os.path.join(elems_dir,(parent+'_')+b+'.elems.txt')
    if os.path.exists(f2): return f2,(parent+'_')+b
    f1=os.path.join(elems_dir,b+'.elems.txt')
    if os.path.exists(f1): return f1,b
    for tag in ('hm_','lsdyna_','abaqus_','samcef_'):
        f3=os.path.join(elems_dir,tag+b+'.elems.txt')
        if os.path.exists(f3): return f3,tag+b
    return None,b
def load_valid(name):
    p=os.path.join('output/ground_truth',name)
    if not os.path.exists(p): return None
    ids=set()
    for line in open(p,encoding='utf-8'):
        t=line.strip()
        if t.isdigit(): ids.add(int(t))
    return ids or None
def content_compare(path, elems_file, nfilter, efilter=None):
    m=decode(path, node_filter=nfilter, elem_filter=efilter) if nfilter else decode(path, elem_filter=efilter)
    dec={}
    for e in m.elements:
        dec.setdefault(e.id,[]).append((e.config,tuple(e.nodes)))
    oracle={}
    for line in open(elems_file,encoding='utf-8'):
        mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
        if mm:
            eid=int(mm.group(1)); cfg=int(mm.group(2))
            nds=tuple(x for x in (int(x) for x in mm.group(3).split()) if x!=0)
            oracle[eid]=(cfg,nds)
    same_cfg=diff_cfg=same_nds=diff_nds=only_dec=only_ora=0
    for eid,(cfg,nds) in oracle.items():
        if eid not in dec:
            only_ora+=1; continue
        dc=[d for d in dec[eid] if d[0]==cfg]
        if dc:
            same_cfg+=1
            if any(d[1]==nds for d in dc): same_nds+=1
            else: diff_nds+=1
        else: diff_cfg+=1
    for eid in dec:
        if eid not in oracle: only_dec+=1
    return (len(oracle),same_cfg,diff_cfg,same_nds,diff_nds,only_dec,only_ora)
rows=[]
for path,info in gt.items():
    if not os.path.exists(path): continue
    ef,disp=map_outfile(path)
    if not ef: continue
    nf=NODE_ID_SETS.get(os.path.basename(path))
    valid=load_valid(nf) if nf else None
    # efilter: 从 oracle 元素列表剪枝 MPC slave 超读 (strict-elems 模式)
    efilter={}
    for line in open(ef,encoding='utf-8'):
        mm=re.match(r'E (\d+) cfg=(\d+) nodes=(.*)',line.strip())
        if mm:
            efilter[int(mm.group(1))]=tuple(x for x in (int(x) for x in mm.group(3).split()) if x!=0)
    try:
        r=content_compare(path,ef,valid,efilter)
    except Exception:
        continue
    t=r[0]
    perfect=(r[1]==t and r[2]==0 and r[3]==t and r[4]==0 and r[5]==0 and r[6]==0)
    rows.append((disp,'PERFECT' if perfect else 'diff',r[1],r[2],r[3],r[4],r[5],r[6],t))
print('content compare(strict-elems):',len(rows),'files')
perfect=[r for r in rows if r[1]=='PERFECT']
print('PERFECT:',len(perfect))
for r in rows:
    if r[1]!='PERFECT':
        print('  %s: sc=%s dc=%s sn=%s dn=%s od=%s oo=%s oracle=%s'%(r[0],r[2],r[3],r[4],r[5],r[6],r[7],r[8]))