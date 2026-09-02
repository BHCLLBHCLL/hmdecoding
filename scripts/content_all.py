import sys,os,json,re,glob
sys.path.insert(0,'hmdecoder')
from decoder import decode
gt=json.load(open('output/ground_truth/corpus_gt.json'))
elems_dir='output/ground_truth/elems'
# 文件名映射: 处理同名碰撞 (父目录前缀)
def map_outfile(path):
    b=os.path.basename(path)
    p=os.path.normpath(path).replace('\\','/')
    # 默认 basename
    f1=os.path.join(elems_dir,b+'.elems.txt')
    if os.path.exists(f1):
        return f1
    # 碰撞前缀 (lsdyna/hm)
    for tag in ('lsdyna_','hm_'):
        f2=os.path.join(elems_dir,tag+b+'.elems.txt')
        if os.path.exists(f2):
            return f2
    return None
def content_compare(path, elems_file):
    m=decode(path)
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
        else:
            diff_cfg+=1
    for eid in dec:
        if eid not in oracle: only_dec+=1
    return (len(oracle),same_cfg,diff_cfg,same_nds,diff_nds,only_dec,only_ora)
rows=[]
for path,info in gt.items():
    if not os.path.exists(path): continue
    ef=map_outfile(path)
    if not ef: continue
    try:
        r=content_compare(path,ef)
    except Exception as ex:
        rows.append((os.path.basename(path),'ERR',str(ex)[:40])); continue
    t=r[0]
    perfect=(r[1]==t and r[2]==0 and r[3]==t and r[4]==0 and r[5]==0 and r[6]==0)
    rows.append((os.path.basename(path),'PERFECT' if perfect else 'diff',r[1],r[2],r[3],r[4],r[5],r[6],t))
print('content compare: %d files'%len(rows))
perfect=[r for r in rows if r[1]=='PERFECT']
print('PERFECT: %d/%d'%(len(perfect),len(rows)))
for r in rows:
    if r[1]!='PERFECT':
        print('  %s: %s sc=%s dc=%s sn=%s dn=%s od=%s oo=%s /%s'%r)