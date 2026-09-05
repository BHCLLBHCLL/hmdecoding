set log [open "D:/training/caedecoder/hmdecoding/output/m3_comp_full.log" w]
proc logit {msg} { global log; puts $log $msg; flush $log }
*readfile "C:/Program Files/Altair/2019/tutorials/hm/cover.hm" 1
*createmark comps 1 "all"
set cids [hm_getmark comps 1]
foreach cid $cids {
  set nm [hm_getvalue comps id=$cid dataname=name]
  set card [hm_getvalue comps id=$cid dataname=cardimage]
  logit "COMP id=$cid name=$nm card=$card"
}
# 元素 -> 组件
*createmark elems 1 "all"
set eids [hm_getmark elems 1]
logit "NELEMS [llength $eids]"
foreach eid [lrange $eids 0 6] {
  set comp [hm_getvalue elems id=$eid dataname=component]
  set cfg [hm_getvalue elems id=$eid dataname=config]
  logit "ELEM id=$eid comp=$comp config=$cfg"
}
logit "DONE"
close $log
*quit 1
