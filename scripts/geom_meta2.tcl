set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/geom_meta2.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/abaqus/geometry.hm" 1} rr
logit "readfile: $rr"
foreach eid {183 184 196 197 198 3837 3838 4116} {
  set cfg "?"; set nodes "?"
  catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
  catch {set nodes [hm_getvalue elements id=$eid dataname=nodes]} _
  logit "eid=$eid config=$cfg nnodes=[llength $nodes] nodes=$nodes"
}
close $log
*quit 1
