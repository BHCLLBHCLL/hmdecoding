set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/cfg_names.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "D:/training/caedecoder/hmdecoding/WS_3.2_3d_tetra_finish.hm" 1
foreach eid {291462 291463 291464 295000 302867} {
  set line "$eid"
  foreach dn {config node1 node2 node3 node4} {
    set v "?"
    catch {set v [hm_getvalue elements id=$eid dataname=$dn]} _
    append line " $dn=$v"
  }
  logit "elem $line"
}
# try template export
catch {*template "nastran"} t1
logit "template nastran: $t1"
catch {*writefile "D:/training/caedecoder/hmdecoding/output/ground_truth/ws_export.fem" 1} t2
logit "writefile fem: $t2"
close $log
*quit 1
