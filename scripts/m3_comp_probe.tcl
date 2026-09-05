set log [open "D:/training/caedecoder/hmdecoding/output/m3_comp.log" w]
proc logit {msg} { global log; puts $log $msg; flush $log }
*readfile "C:/Program Files/Altair/2019/tutorials/hm/cover.hm" 1
*createmark comps 1 "all"
set cids [hm_getmark comps 1]
logit "NUMCOMPS [llength $cids]"
foreach cid $cids {
  set nm [hm_getvalue comps id=$cid dataname=name]
  logit "COMP id=$cid name=$nm"
}
logit "LOOP DONE"
close $log
*quit 1
