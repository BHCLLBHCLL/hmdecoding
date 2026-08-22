set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/lines_dn.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
*readfile "C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm" 1
*createmark points 1 1
foreach dn {id x y z collector} {
  set v "?"
  catch {set v [hm_getvalue points mark=1 dataname=$dn]} _
  logit "point dn=$dn -> $v"
}
*createmark lines 1 1
foreach dn {id collector point1 point2 pt1 pt2 end1 end2 start end} {
  set v "?"
  catch {set v [hm_getvalue lines mark=1 dataname=$dn]} _
  logit "line dn=$dn -> $v"
}
close $log
*quit 1
