set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/ws_allpoints.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "D:/training/caedecoder/hmdecoding/WS_3.2_3d_tetra_finish.hm" 1
*createmark points 1 "all"
set plist [hm_getmark points 1]
foreach pid $plist {
  *createmark points 1 $pid
  set x "?"; set y "?"; set z "?"
  catch {set x [hm_getvalue points mark=1 dataname=x]} _
  catch {set y [hm_getvalue points mark=1 dataname=y]} _
  catch {set z [hm_getvalue points mark=1 dataname=z]} _
  logit "P $pid $x $y $z"
}
close $log
*quit 1
