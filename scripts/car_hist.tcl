set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/car_hist.log" w]
proc logit {msg} { global log; puts $log $msg; flush $log }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/car_section.hm" 1} rr
logit "readfile: $rr"
catch {logit "elem_count=[hm_entityinfo count elements]"}
catch {logit "elem_maxid=[hm_entityinfo maxid elements]"}
set elist ""
catch {*createmark elements 1 "all"} _
catch {set elist [hm_getmark elements 1]} _
logit "total=[llength $elist]"
array set hist {}
foreach eid $elist {
  set cfg "?"
  catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
  if {[info exists hist($cfg)]} {incr hist($cfg)} else {set hist($cfg) 1}
}
foreach cfg [lsort [array names hist]] {
  logit "config $cfg: $hist($cfg)"
}
close $log
*quit 1
