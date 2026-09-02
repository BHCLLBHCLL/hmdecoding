import json,os
gt=json.load(open('output/ground_truth/corpus_gt.json'))
todo=[p for p,v in gt.items() if os.path.exists(p) and v['counts']['elements']>0 and v['counts']['elements']<200000]
done={'joints.hm','seat_2.hm','abaqus_contactManager_2D_tutorial.hm','hook.hm'}
todo=[p for p in todo if p.replace('\\','/').split('/')[-1] not in done]
# 生成每批 Tcl: 15 文件/批
BATCH=15
for bi in range(0,len(todo),BATCH):
    batch=todo[bi:bi+BATCH]
    lines=['# batch %d'%(bi//BATCH),'set outdir "output/ground_truth/elems"']
    for p in batch:
        b=p.replace('\\','/').split('/')[-1]
        lines.append('catch {*readfile "%s" 1} rr_%s'%(p.replace('\\','/'), bi//BATCH))
        # 用独立名字避免冲突
    # 每条路径处理成 probe 块
    body=[]
    for p in batch:
        b=p.replace('\\','/').split('/')[-1]
        body.append('# == %s =='%b)
        body.append('catch {*readfile "%s" 1} rr'%(p.replace('\\','/')))
        body.append('catch {*createmark elements 1 "all"} _')
        body.append('set ids [hm_getmark elements 1]')
        body.append('set of [open "%s/%s.elems.txt" w]'%('output/ground_truth/elems',b))
        body.append('puts $of "count=[llength $ids]"')
        body.append('foreach id $ids {')
        body.append('  set cfg [hm_getvalue elements id=$id dataname=config]')
        body.append('  set nds ""')
        body.append('  foreach dn {node1 node2 node3 node4 node5 node6 node7 node8 node9 node10 node11 node12 node13 node14 node15 node16} {')
        body.append('    set v [hm_getvalue elements id=$id dataname=$dn]')
        body.append('    if {$v eq ""} { break }')
        body.append('    append nds " $v"')
        body.append('  }')
        body.append('  puts $of "E $id cfg=$cfg nodes=$nds"')
        body.append('}')
        body.append('close $of')
        body.append('puts "DONE %s [llength $ids]"'%b)
    tcl='\n'.join(body+['*quit 1'])
    open('scripts/batch_%02d.tcl'%(bi//BATCH),'w').write(tcl)
print('generated', len(range(0,len(todo),BATCH)), 'batches for', len(todo), 'files')