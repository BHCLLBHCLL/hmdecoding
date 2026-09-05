set log [open "D:/training/caedecoder/hmdecoding/output/m3_fa1_elemcomp.log" w]
proc logit {msg} { global log; puts $log $msg; flush $log }
*readfile "C:/Program Files/Altair/2019/tutorials/hm/frame_assembly_1.hm" 1
*createmark elems 1 "all"
set eids [hm_getmark elems 1]
foreach eid $eids {
  set comp [hm_getvalue elems id=$eid dataname=component]
  set prop [hm_getvalue elems id=$eid dataname=property]
  logit "E $eid $comp $prop"
}
close $log
*quit 1
