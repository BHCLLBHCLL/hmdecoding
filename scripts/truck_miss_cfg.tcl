set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/truck_miss_cfg.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/truck.hm" 1} rr
logit "readfile: $rr"

set f [open "D:/training/caedecoder/hmdecoding/output/ground_truth/truck_miss_sample.txt" r]
set eids [split [read $f] "\n"]
close $f

foreach eid $eids {
  if {$eid eq ""} {continue}
  set cfg "?"; set nodes "?"
  catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
  catch {set nodes [hm_getvalue elements id=$eid dataname=nodes]} _
  logit "eid=$eid config=$cfg nnodes=[llength $nodes]"
}
close $log
*quit 1
