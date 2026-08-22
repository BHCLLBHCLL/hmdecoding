set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/geom_verify.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "D:/training/caedecoder/hmdecoding/corpus/synthetic/v1913_geom02_p2.hm" 1
*createmark points 1 "all"
set plist [hm_getmark points 1]
logit "points: $plist"
foreach pid $plist {
  set x "?"; set y "?"; set z "?"
  catch {set x [hm_getvalue points mark=1 dataname=x]} _
  catch {set y [hm_getvalue points mark=1 dataname=y]} _
  catch {set z [hm_getvalue points mark=1 dataname=z]} _
  logit "point $pid: $x $y $z"
}
close $log
*quit 1
