set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/seat_node_meta.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm" 1} rr
logit "readfile: $rr"
catch {logit "node_count=[hm_entityinfo count nodes]"}
catch {logit "node_maxid=[hm_entityinfo maxid nodes]"}
catch {logit "elem_count=[hm_entityinfo count elements]"}
catch {logit "elem_maxid=[hm_entityinfo maxid elements]"}
foreach nid {996 17373 17374 17375 34327 34328 34296 528 529} {
  set x "?"; set y "?"; set z "?"
  catch {set x [hm_getvalue nodes id=$nid dataname=x]} _
  catch {set y [hm_getvalue nodes id=$nid dataname=y]} _
  catch {set z [hm_getvalue nodes id=$nid dataname=z]} _
  logit "node $nid -> x=$x y=$y z=$z"
}
close $log
*quit 1
