set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/ws_probe3.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "D:/training/caedecoder/hmdecoding/WS_3.2_3d_tetra_finish.hm" 1
foreach nid {68519 67604 70576 70468 70307} {
  set x "?"; set y "?"; set z "?"
  catch {set x [hm_getvalue nodes id=$nid dataname=x]} _
  catch {set y [hm_getvalue nodes id=$nid dataname=y]} _
  catch {set z [hm_getvalue nodes id=$nid dataname=z]} _
  logit "node $nid: $x $y $z"
}
foreach eid {302871 302870 302869 302868 302867} {
  set line "$eid"
  foreach dn {node1 node2 node3 node4} {
    set v "?"
    catch {set v [hm_getvalue elements id=$eid dataname=$dn]} _
    append line " $dn=$v"
  }
  logit "elem $line"
}
close $log
*quit 1
