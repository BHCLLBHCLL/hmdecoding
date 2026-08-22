set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/leg_lines2.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm" 1
foreach lid {1 2 4} {
  *createmark lines 1 $lid
  set line "$lid"
  foreach dn {collector points length type p1 p2 node1 node2 nodes x y z} {
    set v "?"
    catch {set v [hm_getvalue lines mark=1 dataname=$dn]} _
    append line " $dn=$v"
  }
  logit "line $line"
}
*createmark points 1 "all"
logit "points: [llength [hm_getmark points 1]]"
close $log
*quit 1
