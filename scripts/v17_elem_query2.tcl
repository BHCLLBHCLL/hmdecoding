# v17 缺失元素 (131508-131767, 589001-589706) 的 config + 节点查询.
set f [open "output/ground_truth/v17_elem_query2.txt" w]
proc logit {msg} { global f; puts $f $msg; flush $f }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/dummy_positioner.hm" 1} rr
logit "readfile: $rr"

# 131508.. 段 (6500113/6500114/2000486/2000949 各段样本)
foreach eid {131508 131509 131510 131511 131630 131632 131633 131634 131683 131684 131685 131687 131688 131694 131700 131757 131758 131760 131766 131767} {
    set cfg "?"; set nds "?"
    catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
    catch {set nds [hm_getvalue elements id=$eid dataname=nodes]} _
    logit "Q eid=$eid config=$cfg nodes=$nds"
}

# 589001.. 段样本
foreach eid {589001 589002 589003 589010 589050 589100 589136 589137 589141 589150 589200 589400 589600 589700 589705 589706} {
    set cfg "?"; set nds "?"
    catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
    catch {set nds [hm_getvalue elements id=$eid dataname=nodes]} _
    logit "R eid=$eid config=$cfg nodes=$nds"
}

# 附加: SHORT 段引用元素
foreach eid {263874 517663 144230 144233 263827 263836} {
    set cfg "?"; set nds "?"
    catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
    catch {set nds [hm_getvalue elements id=$eid dataname=nodes]} _
    logit "S eid=$eid config=$cfg nodes=$nds"
}
close $f
*quit 1
