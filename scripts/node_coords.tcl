set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/node_coords.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm" 1
foreach nid {1 24 25 26 100 151 442 443 465} {
  set x "?"; set y "?"; set z "?"
  catch {set x [hm_getvalue nodes id=$nid dataname=x]} _
  catch {set y [hm_getvalue nodes id=$nid dataname=y]} _
  catch {set z [hm_getvalue nodes id=$nid dataname=z]} _
  logit "node $nid: $x $y $z"
}
close $log
*quit 1
