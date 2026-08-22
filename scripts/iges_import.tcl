set log [open "D:/training/caedecoder/hmdecoding/output/ground_truth/iges_import.log" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
catch {*readfile "D:/training/caedecoder/hmdecoding/corpus/synthetic/minimal.iges" 1} rr
logit "readfile iges: $rr"
foreach ent {points lines surfaces} {
  set n -1
  catch {*createmark $ent 1 "all"} mk
  catch {set n [llength [hm_getmark $ent 1]]} e2
  logit "count $ent: $n"
}
catch {*writefile "D:/training/caedecoder/hmdecoding/corpus/synthetic/v1913_iges_geom.hm" 1} ww
logit "writefile: $ww"
close $log
*quit 1
