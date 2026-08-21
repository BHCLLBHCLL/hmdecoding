set log [open "D:/training/caedecoder/hmdecoding/output/oracle_probe.txt" w]
proc logit {msg} {
  global log
  puts $log $msg
  flush $log
}
logit "oracle probe started"
catch {*readfile "D:/training/caedecoder/hmdecoding/WS_3.2_3d_tetra_finish.hm" 1} rerr
logit "readfile result: $rerr"
foreach ent {nodes elements comps mats props points lines surfaces solids} {
  set n -1
  set mk ""
  catch {*createmark $ent 1 "all"} mk
  catch {set n [llength [hm_getmark $ent 1]]} e2
  logit "$ent mark_result=[string trim $mk] count=$n err=$e2"
}
catch {set modelinfo [hm_info modelinfo]} mi
logit "modelinfo: $modelinfo err=$mi"
close $log
*quit 1
