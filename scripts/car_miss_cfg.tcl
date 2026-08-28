set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/car_miss_cfg.log" w]
proc logit {msg} { global log; puts $log $msg; flush $log }
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/car_section.hm" 1} rr
logit "readfile: $rr"
catch {logit "elem_count=[hm_entityinfo count elements]"}
foreach eid {6885 6886 6889 6911 6920 6956 10614 11310 20038 20136 25201 25220 27905 28000 28438 28443 28500 28511 3117 3118 19} {
  set cfg "?"; set nodes "?"
  catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
  catch {set nodes [hm_getvalue elements id=$eid dataname=nodes]} _
  logit "eid=$eid config=$cfg nnodes=[llength $nodes] nodes=$nodes"
}
close $log
*quit 1
