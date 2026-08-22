set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/iges_import2.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
catch {*readfile "C:/Program Files/Altair/2019/tutorials/hm/bumper_end.iges" 1} rr
logit "readfile bumper_end.iges: $rr"
foreach ent {points lines surfaces} {
  set n -1
  catch {*createmark $ent 1 "all"} mk
  catch {set n [llength [hm_getmark $ent 1]]} e2
  logit "count $ent: $n"
}
close $log
*quit 1
