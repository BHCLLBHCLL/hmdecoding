set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/node_many.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm" 1
foreach nid {24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 50 60 70 80 90 100 120 140 160 180 200 250 300 350 400 440 442 443 460 465} {
  set x "?"; set y "?"; set z "?"
  catch {set x [hm_getvalue nodes id=$nid dataname=x]} _
  catch {set y [hm_getvalue nodes id=$nid dataname=y]} _
  catch {set z [hm_getvalue nodes id=$nid dataname=z]} _
  logit "$nid $x $y $z"
}
close $log
*quit 1
