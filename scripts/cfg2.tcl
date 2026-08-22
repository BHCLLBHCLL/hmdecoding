set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/cfg2.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "D:/training/caedecoder/hmdecoding/WS_3.2_3d_tetra_finish.hm" 1
foreach eid {300000 305000 310000 315000 320000} {
  set line "$eid"
  foreach dn {config node1 node2 node3 node4} {
    set v "?"
    catch {set v [hm_getvalue elements id=$eid dataname=$dn]} _
    append line " $dn=$v"
  }
  logit "elem $line"
}
close $log
*quit 1
