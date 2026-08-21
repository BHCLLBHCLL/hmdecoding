set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/elem_all.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm" 1
*createmark elements 1 "all"
set elist [hm_getmark elements 1]
logit "count [llength $elist]"
foreach eid $elist {
  set n1 "?"; set n2 "?"; set n3 "?"; set n4 "?"
  catch {set n1 [hm_getvalue elements id=$eid dataname=node1]} _
  catch {set n2 [hm_getvalue elements id=$eid dataname=node2]} _
  catch {set n3 [hm_getvalue elements id=$eid dataname=node3]} _
  catch {set n4 [hm_getvalue elements id=$eid dataname=node4]} _
  logit "$eid $n1 $n2 $n3 $n4"
}
close $log
*quit 1
