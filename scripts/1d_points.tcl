set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/1d_points.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm" 1
*createmark points 1 "all"
set plist [hm_getmark points 1]
logit "points: $plist"
foreach pid $plist {
  *createmark points 1 $pid
  set x "?"; set y "?"; set z "?"
  catch {set x [hm_getvalue points mark=1 dataname=x]} _
  catch {set y [hm_getvalue points mark=1 dataname=y]} _
  catch {set z [hm_getvalue points mark=1 dataname=z]} _
  logit "point $pid: $x $y $z"
}
close $log
*quit 1
