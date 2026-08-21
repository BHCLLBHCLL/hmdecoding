set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/ws_probe2.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "D:/training/caedecoder/hmdecoding/WS_3.2_3d_tetra_finish.hm" 1
catch {*createmark nodes 1 "all"} m1
set nlist [hm_getmark nodes 1]
logit "node ids sample: [lrange $nlist 0 4]"
foreach nid [lrange $nlist 0 2] {
  set x "?"
  catch {set x [hm_getvalue nodes id=$nid dataname=x]} _
  logit "node $nid x=$x"
}
catch {*createmark elements 1 "all"} m2
set elist [hm_getmark elements 1]
logit "elem ids sample: [lrange $elist 0 4]"
foreach eid [lrange $elist 0 2] {
  set cfg "?"
  catch {set cfg [hm_getvalue elements id=$eid dataname=config]} _
  logit "elem $eid config=$cfg"
}
# try hm_entityinfo alternative
set v ""
catch {set v [hm_entityinfo entities nodes]} _
logit "hm_entityinfo nodes: [string range $v 0 100]"
close $log
*quit 1
