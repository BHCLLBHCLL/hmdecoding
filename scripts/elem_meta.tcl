set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/elem_meta.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "D:/training/caedecoder/hmdecoding/WS_3.2_3d_tetra_finish.hm" 1
foreach eid {302871 302867 300000 305000 310000 320000 324028} {
  set line "$eid"
  foreach dn {config name comp} {
    set v "?"
    catch {set v [hm_getvalue elements id=$eid dataname=$dn]} _
    append line " $dn=$v"
  }
  logit "elem $line"
}
*createmark nodes 1 "all"
logit "node count: [llength [hm_getmark nodes 1]]"
close $log
*quit 1
