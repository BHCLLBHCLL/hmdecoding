set log [open "D:/training/caedecoder/hmdecoding/output/m3_elem_comp2.log" w]
proc logit {msg} { global log; puts $log $msg; flush $log }
*readfile "C:/Program Files/Altair/2019/tutorials/hm/cover.hm" 1
foreach eid {1 2 589 590 604 605 764} {
  set comp [hm_getvalue elems id=$eid dataname=component]
  set cfg [hm_getvalue elems id=$eid dataname=config]
  logit "ELEM id=$eid comp=$comp config=$cfg"
}
close $log
*quit 1
