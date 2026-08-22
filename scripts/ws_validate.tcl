set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/ws_validate.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "D:/training/caedecoder/hmdecoding/WS_3.2_3d_tetra_finish.hm" 1
foreach eid {291462 291500 292000 295000 300000 302000 304000 306000 308000 310000 312000 314000 316000 318000 320000 322000 324000 302871 302736 302735} {
  set line "$eid"
  foreach dn {config node1 node2 node3 node4} {
    set v "?"
    catch {set v [hm_getvalue elements id=$eid dataname=$dn]} _
    append line " $dn=$v"
  }
  logit "elem $line"
}
foreach nid {67604 68519 70307 70468 70576 70098 70393 68911 71000 69000} {
  set x "?"; set y "?"; set z "?"
  catch {set x [hm_getvalue nodes id=$nid dataname=x]} _
  catch {set y [hm_getvalue nodes id=$nid dataname=y]} _
  catch {set z [hm_getvalue nodes id=$nid dataname=z]} _
  logit "node $nid: $x $y $z"
}
close $log
*quit 1
