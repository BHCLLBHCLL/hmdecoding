set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/car_cfg3.log" w]
proc logit {msg} { global log; puts $log $msg; flush $log }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/car_section.hm" 1} rr
logit "readfile: $rr"
set elist ""
catch {*createmark elements 1 "all"} _
catch {set elist [hm_getmark elements 1]} _
set n 0
foreach eid $elist {
  set cfg "?"
  catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
  if {$cfg == 3} {
    set nodes "?"
    catch {set nodes [hm_getvalue elements id=$eid dataname=nodes]} _
    logit "eid=$eid config=3 nodes=$nodes"
    incr n
  }
}
logit "total config3: $n"
close $log
*quit 1
