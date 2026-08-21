set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/leg_coords.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm" 1
*createmark nodes 1 "all"
set nlist [hm_getmark nodes 1]
logit "node ids: $nlist"
foreach nid $nlist {
  set x "?"
  set y "?"
  set z "?"
  catch {set x [hm_getvalue nodes id=$nid dataname=x]} _
  catch {set y [hm_getvalue nodes id=$nid dataname=y]} _
  catch {set z [hm_getvalue nodes id=$nid dataname=z]} _
  logit "node $nid: $x $y $z"
}
*createmark lines 1 "all"
set llist [hm_getmark lines 1]
logit "line ids: $llist"
foreach lid $llist {
  set p1 "?"
  set p2 "?"
  catch {set p1 [hm_getvalue lines id=$lid dataname=p1]} _
  catch {set p2 [hm_getvalue lines id=$lid dataname=p2]} _
  logit "line $lid: p1=$p1 p2=$p2"
}
close $log
*quit 1
