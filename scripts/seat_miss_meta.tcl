set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/seat_miss_meta.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm" 1} rr
logit "readfile: $rr"
foreach eid {27499 27500 27501 27502 27503} {
  set cfg "?"; set nodes "?"
  catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
  catch {set nodes [hm_getvalue elements id=$eid dataname=nodes]} _
  logit "eid=$eid config=$cfg nnodes=[llength $nodes] nodes=$nodes"
}
close $log
*quit 1
