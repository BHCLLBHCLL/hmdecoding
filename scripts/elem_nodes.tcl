set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/elem_nodes.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm" 1
foreach eid {198 199 200 201 202 203 204} {
  set line "$eid"
  foreach dn {config node1 node2 node3 node4 node5 node6 node7 node8} {
    set v "?"
    catch {set v [hm_getvalue elements id=$eid dataname=$dn]} _
    append line " $dn=$v"
  }
  logit "elem $line"
}
close $log
*quit 1
