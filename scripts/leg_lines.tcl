set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/leg_lines.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm" 1
foreach lid {1 2 4} {
  set line "$lid"
  foreach dn {name length type p1 p2 node1 node2 nodes} {
    set v "?"
    catch {set v [hm_getvalue lines id=$lid dataname=$dn]} _
    append line " $dn=$v"
  }
  logit "line $line"
}
# points? 0 points. check nodes used by lines via geometry
close $log
*quit 1
