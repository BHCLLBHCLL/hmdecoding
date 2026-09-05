set log [open "D:/training/caedecoder/hmdecoding/output/m3_fa1_comps.log" w]
proc logit {msg} { global log; puts $log $msg; flush $log }
*readfile "C:/Program Files/Altair/2019/tutorials/hm/frame_assembly_1.hm" 1
*createmark comps 1 "all"
set cids [hm_getmark comps 1]
logit "NUMCOMPS [llength $cids]"
foreach cid $cids {
  set nm [hm_getvalue comps id=$cid dataname=name]
  logit "COMP id=$cid name=$nm"
}
# 元素->comp 采样 (每段边界)
foreach eid {1 10861} {
  set comp [hm_getvalue elems id=$eid dataname=component]
  logit "ELEM id=$eid comp=$comp"
}
close $log
*quit 1
