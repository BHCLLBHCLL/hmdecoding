# v17 特殊/缺失元素查询: config + 节点连接关系.
set f [open "output/ground_truth/v17_elem_query.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/dummy_positioner.hm" 1} rr
logit "readfile: $rr"

# 特殊段首元素 (SHORT 段样本 + OK 特殊段)
set special {3912279 3912289 365000 144234 1009536 263825 263836 52 500002 200002}
foreach eid $special {
    set cfg "?"; set nds "?"
    catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
    catch {set nds [hm_getvalue elements id=$eid dataname=nodes]} _
    logit "SPEC eid=$eid config=$cfg nodes=$nds"
}

# 低 ID 段缺失元素样本 (1..410k 缺失带的头部/中部/尾部)
foreach eid {1 2 3 100 1000 10000 50000 100000 200000 300000 400000 409000 409115} {
    set cfg "?"; set nds "?"
    catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
    catch {set nds [hm_getvalue elements id=$eid dataname=nodes]} _
    logit "LOW eid=$eid config=$cfg nodes=$nds"
}

# 缺失节点 3481964/3481965 坐标
foreach nid {3481964 3481965} {
    set x "?"; set y "?"; set z "?"
    catch {set x [hm_getvalue nodes id=$nid dataname=x]} _
    catch {set y [hm_getvalue nodes id=$nid dataname=y]} _
    catch {set z [hm_getvalue nodes id=$nid dataname=z]} _
    logit "NODE nid=$nid x=$x y=$y z=$z"
}
close $f
*quit 1
